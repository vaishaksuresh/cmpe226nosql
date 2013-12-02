require 'neography'
require 'zlib'
require 'yajl'
require 'logger'
 
gz = File.open('../data/2013-11-15-0.json.gz', 'r')
js = Zlib::GzipReader.new(gz).read
@neo = Neography::Rest.new({:server => "192.168.0.20"})

class GithubEvent
  def initialize(event, neo)
    @event = event
    @type = @event["type"]
    @neo = neo
    @log = Logger.new(STDOUT)
    @event_to_relationships = {
      "WatchEvent" => "watch",
      "ForkEvent" => "fork",
      "PullRequestEvent" => "pull_request",
      "PushEvent" => "push",
    }
  end

  def relevant?
    @relevant_events ||= @event_to_relationships.keys
    @relevant_events.include?(@type)
  end

  def process
    if relevant?
      @log.debug("Processing #{@type} which was created at #{@event["created_at"]}")
    else
      @log.debug("Skipping #{@type}")
      return nil
    end
    
    actor_attrs = @event["actor_attributes"].merge({"_type" => "actor"})
    repo_attrs = @event["repository"].merge({"_type" => "repository"})

    actor_node = find_or_create_node("actors", "login", @event["actor"], actor_attrs)
    repo_node = find_or_create_node("repositories", "url", @event["repository"]["url"], repo_attrs)

    rel_attrs = [@event_to_relationships[@type], actor_node, repo_node]
    rel_desc =  [@event["actor"], @type, @event["repository"]["url"]].join('-')
    rel_node = find_or_create_relationship("relationships", "description", rel_desc, rel_attrs)

    @log.debug("Relationship #{rel_node} found or created")
    @log.info("Event processed successfully")
    
  rescue => e
    @log.warn("Failed to process #{@type} which was created at #{@event["created_at"]}")
    @log.debug(e)
  end


  # Retrieve node from idx. If it doesn't exist, create it and add to the idx.
  def find_or_create_node(*args)
    i, k, v, attrs = *args
    node = @neo.get_node_index(i, k, v) rescue nil
    if node
      @log.debug("Found node #{v}")
      return node
    end

    @log.info("Node #{v} doesn't exist, creating it")
    node = @neo.create_node(attrs)
    @neo.add_node_to_index(i, k, v, node)
    return node
  end

  def find_or_create_relationship(*args)
    i, k, v, attrs = *args
    rel = @neo.get_relationship_index(i, k, v) rescue nil
    if rel
      @log.debug("Found rel #{v}")
      return rel
    end

    @log.info("Rel #{v} doesn't exist, creating it")
    rel = @neo.create_relationship(*attrs)
    @neo.add_relationship_to_index(i, k, v, rel)
    return rel
  end
end

range = (1..1)
i, j = range.first, range.last
Yajl::Parser.parse(js) do |event|
  i += 1; break if i > j
  GithubEvent.new(event, @neo).process
end

class Object
  def itself
    self
  end
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

  def recommend_actors_to_follow
    require_existence!

    repos = @node.outgoing(:watch).map(&:itself)
    other_actors = repos.flat_map{|r| r.incoming(:watch).map(&:itself)}.uniq
    other_actors.delete_if{|a| @name == a.login}
    other_actors
  end

  def require_existence!
    raise "Actor #{@name} doesn't exist" unless exists?
  end
end

require 'irb'
IRB.start
