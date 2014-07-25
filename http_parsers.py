#
# Copyright Michael Groys, 2012-2014
#

#
# This file implements HTTP request and response parser
# It uses python package mimetools to implement the logic
#

import urlparse
import mimetools
from StringIO import StringIO
import m.common as common

class HttpCommon(object):
    def _parseHeaders(self, headers):
        self.headers = mimetools.Message(StringIO(headers))

class HttpRequest(HttpCommon):
    def __init__(self, data):
        if not data:
            raise common.MiningError("Empty request")
        try:
            request, headers = data.split('\r\n', 1)
        except:
            raise common.MiningError("Failed to split request header: %s" % data)
          
        #print "====Start headers==="
        #print headers
        #print "--------------------"
        self._parseHeaders(headers)
        elements = request.split(' ')
        if len(elements)<3:
            raise common.MiningError("Invalid http request line: '%s'" % request)
        self.method = elements[0]
        self.relUrl = elements[1]
        self.httpVersion = elements[-1] # allows multiples spaces separating url and http version
        if not self.method or not self.relUrl or not self.httpVersion:
            raise common.MiningError("Failed to parse http request line: '%s'" % request)
        self._parseUrl()

    @property
    def userAgent(self):
        return self.headers.get("user-agent", None)
    def _parseUrl(self):
        self.parsedUrl = urlparse.urlparse(self.relUrl, "http")
        if self.relUrl.startswith("http://"):
            # proxy request
            self.fullUrl = self.relUrl
            self.relUrl = self.parsedUrl.path
            if self.parsedUrl.query:
                self.relUrl += "?" + self.parsedUrl.query
            self.host = self.parsedUrl.netloc
        else:
            self.fullUrl = "http://" + self.host + self.relUrl
            self.host = self.headers.get("Host", "")
        self.paramLists = urlparse.parse_qs(self.parsedUrl.query, keep_blank_values=True)
        self.params = {}
        for name, pList in self.paramLists.iteritems():
            self.params[name] = pList[-1]
        self._pathComponents = None
    @property
    def pathComponents(self):
        if self._pathComponents is not None:
            return self._pathComponents
        self._pathComponents = self.parsedUrl.path.split("/")
        return self._pathComponents
    @property
    def path(self):
        return self.parsedUrl.path
    def __str__(self):
        s = self.method + " http://"+ (self.host if self.host else "?.?.?.?") + self.relUrl 
        range = self.headers.get("range")
        if range:
            s += " range=" + range
        return s

class HttpResponse(HttpCommon):
    def __init__(self, data):
        if not data:
            raise common.MiningError("Empty response")
        try:
            response, headers = data.split('\r\n', 1)
        except:
            raise common.MiningError("Failed to split response header: %s" % data)
            
        self._parseHeaders(headers)

        elements = response.split(' ', 2)
        if len(elements) < 2:
            raise common.MiningError("Failed to parse http response status line: %s" % response)
        self.httpVersion = elements[0]
        
        statusCodeStr = elements[1]
        self.statusString = elements[2] if len(elements)>2 else ""
            
        self.statusCode = int(statusCodeStr)
        cl = self.headers.get("content-length", "")
        cl = cl.strip()
        if cl.isdigit():
            self.length = int(cl)
        else:
            self.length = -1
    @property
    def contentType(self):
        return self.headers.gettype()
    def __str__(self):
        s = "%d %s clen=%d ctype=%s" % (self.statusCode, self.statusString, self.length, self.contentType)
        range = self.headers.get("content-range")
        if range:
            s += " range=" + range
        return s

class Url(object):
    def __init__(self, data):
        self.parsedUrl = urlparse.urlparse(data, "http")
        self.paramLists = urlparse.parse_qs(self.parsedUrl.query, keep_blank_values=True)
        self.params = {}
        for name, pList in self.paramLists.iteritems():
            self.params[name] = pList[-1]
        self._components = None
    @property
    def components(self):
        """list of url path components"""
        if self._components is not None:
            return self._components
        self._components = self.parsedUrl.path.split("/")
        return self._components
    @property
    def path(self):
        """Path part of url"""
        return self.parsedUrl.path
    @property
    def host(self):
        return self.parsedUrl.netloc
    def __str__(self):
        s = "host=%s path=%s params=[" % (self.host, self.parsedUrl.path)
        s += " ".join("%s=%s" % (param,value) for (param,value)  in self.params.iteritems())
        s += "]"
        return s

