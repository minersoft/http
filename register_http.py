import miner_globals
import http_parsers

# Completion symbols
miner_globals.addCompletionSymbol('request', http_parsers.HttpRequest("GET / HTTP/1.1\r\n\r\n"))
miner_globals.addCompletionSymbol('response', http_parsers.HttpResponse("HTTP/1.1 200 OK\r\n\r\n"))
miner_globals.addCompletionSymbol('url', http_parsers.Url("http://host:80/path?var=value"))

# Add to parser
miner_globals.addParserClassMapping("request", "http_parsers.HttpRequest", "http request header")
miner_globals.addParserClassMapping("response", "http_parsers.HttpResponse", "http response header")
miner_globals.addParserClassMapping("url", "http_parsers.Url", "URL string")
