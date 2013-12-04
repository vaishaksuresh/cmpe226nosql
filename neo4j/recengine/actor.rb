require 'term/ansicolor'
class String
  include Term::ANSIColor
end

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

    current_user_login = node.login
    recommendations = []
    actors = [@node]
    
    level_rels = []
    while level > 0
      level_rels << actors.map do |a|
        repos = a.rels.map do |r|
          {r.end_node => r.rel_type}
        end.reduce(&:merge)

        repos_for_this_actor = repos.map do |repo, src_rel_type|
          connected_actors = repo.rels.map do |r|
            if r.start_node.login == current_user_login
              {}
            else
              {r.start_node => r.rel_type}
            end
          end.reduce(&:merge)
          no_of_rels = repo.rels.count
          src_weight = weight_map(src_rel_type)

          weighed_actors = connected_actors.map do |a, dest_rel_type|
            {
              a => {
                "weight" => src_weight * weight_map(dest_rel_type),
                "reason" => dest_rel_type
              }
            }
          end.reduce(&:merge)

          {repo => weighed_actors || {}}
        end.reduce(&:merge)
      end
      level -= 1
    end
    return level_rels

    ##################################################
    # {                                              #
    #   {                                            #
    #     actor => [                                 #
    #               repo => {actor => 1, actor => 5} #
    #               repo2 => {actor => 3}            #
    #              ],                                #
    #     actor2 => []                               #
    #   }                                            #
    #   {                                            #
    #   }                                            #
    # }                                              #
    ##################################################
    

    #######################################################
    # while level > 0                                     #
    #   recs_from_this_level = actors.map do |actor|      #
    #     actor.                                          #
    #       outgoing.map(&:itself).                       #
    #       map{|r| {r => r.incoming.map(&:itself)}}      #
    #       delete_if{|a| @name == a.login} # delete self #
    #   end                                               #
    #   recommendations << recs_from_this_level           #
    #   actors = recs_from_this_level                     #
    #   level -= 1                                        #
    # end                                                 #
    #######################################################


  end

  

  def flat_actors
    flat_actors = []
    result_set = _span_out(1)
    
    result_set.each_with_index do |level, level_i|
      level.each do |src_actor|
        src_actor.each do |repo, dest_actors|
          dest_actors.each do |dest_actor, attrs|
            flat_actors << {
              "login" => dest_actor.login,
              "weight" => attrs["weight"],
              "reason" => attrs["reason"],
              "via_repo" => repo.url.gsub("https://github.com/", ""),
              "level" => level_i,
            }
          end
        end
      end
    end

    return flat_actors
  end

  require 'term/ansicolor'

  def formatted_recommenation
    sorted_actors = flat_actors.sort {|a,b| a["weight"] <=> b["weight"]}
    sorted_actors.reverse.each do |actor|
      c1 = if actor["weight"] <= 1
             :cyan
           elsif actor["weight"] <= 2
             :yellow
           elsif actor["weight"] <= 4
             :blue
           elsif actor["weight"] > 4
             :green
           end
      printf("user:%35s\t[level of separation: #{actor["level"]}]\t[score: #{actor["weight"]}]\t[via_repo: #{actor["via_repo"]}]".send(c1), actor["login"])
      printf("\t[reason: %s]\n", actor["reason"].black.send("on_#{c1}"))
    end
    nil
  end



  def weight_map(rel)
    {"watch" => 1, "fork" => 2, "pull_request" => 4, "push" => 8}[rel]
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

