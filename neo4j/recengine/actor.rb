class Actor
  attr_reader :node

  def initialize(name, neo)
    @name = name
    @neo = neo
    @log = Logger.new(STDOUT)
  end

  def inspect
    "#{@name} [#{@node}]"
  end

  def load
    @node ||= Neography::Node.find("actors", "login", @name, @neo) rescue nil
  end

  def exists?
    load
    !!@node
  end

  def recommend_actors_to_follow(level=1)
    recs = _span_out(level)
    recs.map!(&:login)
    puts recs
    puts "Total actors: #{recs.length}"
  end

  def _span_out(level)
    require_existence!

    recommendations = []
    actors = [@node]

    while level > 0
      recs_from_this_level = actors.flat_map do |a|
        a.outgoing.map(&:itself).
          flat_map{|r| r.incoming.map(&:itself)}.
          uniq.
          delete_if{|a| @name == a.login}
      end
      recommendations << recs_from_this_level
      actors = recs_from_this_level
      level -= 1
    end

    recommendations.flatten.uniq
  end

  def require_existence!
    raise "Actor #{@name} doesn't exist" unless exists?
  end
end

class Object
  def itself
    self
  end
end

