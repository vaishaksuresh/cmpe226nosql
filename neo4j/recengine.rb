#!/usr/bin/env ruby

####################################################################
# Installation instructions --                                     #
# This script should use Bundler, but to keep things simple        #
# for now we aren't using it.                                      #
# Ensure that you are running a Ruby version 1.9.2.                #
#                                                                  #
# Install required gems like this --                               #
# `gem install yajl-ruby mixlib-cli neography`                     #
#                                                                  #
# Then run the script in `load` mode --                            #
# `./recengine.rb -x load -d ../path/to/data/dir -s server.com`    #
#                                                                  #
# After loading sufficient data, run it in the interactive mode -- #
# `./recengine.rb -s server.com`                                   #
####################################################################

require 'irb'
require 'zlib'
require 'yajl'
require 'mixlib/cli'

require_relative './recengine/github_event'
require_relative './recengine/actor'

class RecEngine
  include Mixlib::CLI

  option :execute,
    :short => "-x CMD",
    :long  => "--execute CMD",
    :default => 'interactive',
    :description => "Mode of operation. Possible values: `load`, `interactive`"

  option :server,
    :short => "-s SERVER",
    :long  => "--server SERVER",
    :default => 'localhost',
    :description => "Hostname of the Neo4j server"

  option :port,
    :short => "-p PORT",
    :long  => "--port PORT",
    :default => '7474',
    :description => "Port of the Neo4j server"

  option :data,
    :short => "-d DATA",
    :long  => "--data DATA",
    :description => "Data files or directores to be loaded into Neo4j. "\
  "These have to be gzipped json format like the ones downloaded from githubarchive.org"

  option :limit_entries_per_file,
    :short => "-l LIMIT",
    :long => "--limit-entries-per-file LIMIT",
    :description => "Read only these many entries from a data file before moving on to the next one"
end

cli = RecEngine.new
cli.parse_options

@neo = Neography::Rest.new({:server => cli.config[:server],
                             :port => cli.config[:port],
                             :log_enabled => true})
@log = Logger.new(STDOUT)

if cli.config[:execute] == "load"

  raise "No data files or directories supplied for loading" unless cli.config[:data]
  if File.file?(cli.config[:data])
    data_files = [cli.config[:data]]
  elsif File.directory?(cli.config[:data])
    file_exp = File.join(cli.config[:data], "**", "*.gz")
    data_files = Dir.glob(file_exp)
  else
    raise "No data files or directories supplied for loading"
  end

  data_files.each do |fl|
    @log.info("Reading file #{fl}")

    gz = File.open(fl, 'r')
    js = Zlib::GzipReader.new(gz).read

    i = 0
    limit = cli.config[:limit_entries_per_file]
    Yajl::Parser.parse(js) do |event|
      i += 1; break if limit && i > limit
      GithubEvent.new(event, @neo).process
    end
  end

elsif cli.config[:execute] == "interactive"
  Object.send(:remove_const, :ARGV)
  ARGV = []
  def recommendations_for(u, l=1)
    Actor.new(u, @neo).recommend_actors_to_follow(l)
  end
  puts "\n\n###\nSample usage: recommendations_for('user-name')"
  puts "Can also be parameterized for levels: recommendations_for('user-name', 2)\n###\n\n"
  IRB.start
else
  raise "Cannot execute #{cli.config[:execute]}"
end
