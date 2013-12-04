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
    @log.info("Spanning out from #{node.login}")

    current_user_login = node.login
    recommendations = []
    source_actors = [@node]
    
    level_rels = []
    while level > 0
      @log.info("Processing level #{level} with #{source_actors.length} source actors")
      next_source_actors = []
      level_rels << source_actors.map do |a|
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

          next_source_actors << connected_actors.keys
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

      source_actors = next_source_actors.dup.flatten
      level -= 1
    end
    @log.info("Spanning out complete")
    return level_rels
  end

  def flat_actors(l=1)
    @log.info("Checking for memoized flattened recommendations")
    @memoized_flat_result ||= {}
    return @memoized_flat_result[l] if @memoized_flat_result[l]

    @log.info("Commencing flattening for level #{l}")
    _flat_actors = []
    result_set = _span_out(l)
    
    result_set.each_with_index do |level, level_i|
      level.each do |src_actor|
        src_actor.each do |repo, dest_actors|
          dest_actors.each do |dest_actor, attrs|
            _flat_actors << {
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

    @log.info("Grouping users by login name")
    final_result = _flat_actors.
      uniq.
      group_by{|a| a["login"]}.
      map{|actor, details| {actor => details, 
        "score" => details.map{|e| e["weight"]}.reduce(:+)
      }}.
      sort{|a, b| b["score"] <=> a["score"]}
    
    @log.info("Memoizing result for level #{l}")
    @memoized_flat_result.merge!(l => final_result)
    return flat_actors(l)
  end

  require 'term/ansicolor'

  def formatted_recommendation(l=1)
    actors = flat_actors(l)
    colors = ColorMap.new(actors.length)

    @log.info("Formatting first 100 of #{actors.length} entries")
    actors.first(100).each_with_index do |actor, i|
      c = colors.map(i)
      printf("score: %d ".send(c), actor["score"])
      login = actor.keys.find{|k| k != "score"}
      printf("\tgithub login: %s\n".send(c), login)
      actor[login].each do |lineitem|
        printf("\t[level of separation: #{lineitem["level"]}]\t[score: #{lineitem["weight"]}]\t[via_repo: #{lineitem["via_repo"]}]".send(c))
        printf("\t[reason: %s]\n", lineitem["reason"].black.send("on_#{c}"))
      end
    end
    nil
  end

  def weight_map(rel)
    {"watch" => 1, "fork" => 2, "pull_request" => 4, "push" => 8}[rel]
  end

  def require_existence!
    raise "Actor #{@name} doesn't exist" unless exists?
  end

  class ColorMap
    def initialize(max)
      @max = max
      @thresholds = [
                     0,
                     (max * 0.1).ceil,
                     (max * 0.5).ceil,
                     (max * 0.7).ceil
                    ]
    end

    def map(idx)
      return :green  if (@thresholds[0]..@thresholds[1]).include?(idx)
      return :blue   if (@thresholds[1]..@thresholds[2]).include?(idx)
      return :yellow if (@thresholds[2]..@thresholds[3]).include?(idx)
      return :cyan
    end
  end
end


class Object
  def itself
    self
  end
end

