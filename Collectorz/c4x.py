#!/usr/bin/python

# this takes an XML export file from the Collectorz Movie software and
# generates NFO files, in my case for Plex. It can be picky, but does work




from xml.dom import minidom
from xml.dom.minidom import Document
import os
import shutil
#import wget 
import urllib

xmldoc = minidom.parse("export.xml")


server = "" # "http://192.168.1.41:81/" # If it is blank then do not copt to local directory
#imagesDir = "/Volumes/Media/Images/"	# This is where all thumbnails and fanart are stored. 
imagesDir = ""

if len(imagesDir) > 0:
  if not os.path.exists(imagesDir):
    os.makedirs(imagesDir)


savedFiles = 0
movieCount = 0


#/mnt/homevol/media/Movies/images
#root@gv2:/mnt/homevol/media/Movies/images# python -m SimpleHTTPServer

def fixfilename (fn):
# Remove file:// and %20 from filename...

  fn = fn.replace ("file://","")
  fn = fn.replace ("%20"," ")
#  print "New FN", fn
  return fn
  
def myCopy (fnFrom, fnTo):

  if os.path.isfile (fnFrom):
    # From MUST exist...
    #(filepath, filename) = os.path.split(fnTo)
    #if os.path.exists (filepath):
      if os.path.isfile (fnTo):
        if os.path.getsize (fnFrom) != os.path.getsize (fnTo):
          "One of us is not the same", fnFrom, fnTo
          shutil.copyfile (fnFrom, fnTo)
        #else:
        #  shutil.copyfile (fnFrom, fnTo)
      else:
          shutil.copyfile (fnFrom, fnTo)
      
    #else:
    #  print "Directory does not exist for:", fnTo

def processMovies(movie):

      global savedFiles
      global movieCount

      doc = Document()
      #outLevel1 = doc.createElement("videodb")

      name = doc.createElement("version")
      name.appendChild (doc.createTextNode("1"))


      m = {}
      m['originaltitle'] = ""
      m['title'] = ""
      m['plot'] = ""
      m['runtime'] = ""
      m['mpaa'] = "NR"
      m['rating'] = ""
      m['id'] = ""
      m['trailer'] = ""
      m['studio'] = ""
      m['url'] = ""
      m['path'] = ""
      m['filenameandpath'] = ""
      m['basepath'] = ""
      m['coverfront'] = ""
      m['episodecount'] = 0
      m['format'] = ""
      m['collectionstatus'] = ""
      m['backgroundbackdrop'] = ''
      
      #print movie.nodeName
      mov = doc.createElement("movie")

      for kids in movie.childNodes:


        # title: <title> <= <title>
        if kids.nodeName == "title":
          # title <= title; direct 
          m['title'] = kids.childNodes[0].nodeValue.encode('ascii', errors='backslashreplace')
          name = doc.createElement("title")
          name.appendChild (doc.createTextNode(m ['title'].encode('ascii', errors='backslashreplace')))
          mov.appendChild (name)
          

        # Movie Plot: <plot> <= <plot>
        if kids.nodeName == "plot":
          m['plot'] = kids.childNodes[0].nodeValue
          name = doc.createElement("plot")
          name.appendChild (doc.createTextNode(m ['plot'].encode('ascii', errors='backslashreplace')))
          mov.appendChild (name)

        # Run Time - In Minutes: <runtime> <= <runtime>  
        if kids.nodeName == "runtime":
          m['runtime'] = kids.childNodes[0].nodeValue
          name = doc.createElement("runtime")
          name.appendChild (doc.createTextNode(m ['runtime'].encode('ascii', errors='backslashreplace')))
          mov.appendChild (name)

        # collectionstatus: <> <= <collectionstatus>  
        if kids.nodeName == "collectionstatus":
          m['collectionstatus'] = kids.childNodes[0].nodeValue

        # background image: <> <= <backgroundbackdrop>
        if kids.nodeName == "backgroundbackdrop":
          m['backgroundbackdrop'] = kids.childNodes[0].nodeValue

        if kids.nodeName == "coverfront":
          m['coverfront'] = kids.childNodes[0].nodeValue
          #print m['coverfront']

        # MPAA Rating: <mpaa> <= <mpaarating><displayname>
        if kids.nodeName == "mpaarating":
          for r in kids.childNodes:
            if r.nodeName == "displayname":
              m['mpaa'] = r.childNodes[0].nodeValue
              

        # Media Format: <> <= <format><displayname> - For Info only
        if kids.nodeName == "format":
          for r in kids.childNodes:
            if r.nodeName == "displayname":
              m['format'] = r.childNodes[0].nodeValue

        # Country: <country> <= <country><displayname>
        if kids.nodeName == "country":
          for r in kids.childNodes:
            if r.nodeName == "displayname":
              name = doc.createElement("country")
              name.appendChild (doc.createTextNode(r.childNodes[0].nodeValue.encode('ascii', errors='backslashreplace')))
              mov.appendChild (name)

        # IMDB Rating: <rating> <= <imdbrating>
        if kids.nodeName == "imdbrating":
          m['rating'] = kids.childNodes[0].nodeValue
          name = doc.createElement("rating")
          name.appendChild (doc.createTextNode(m ['rating'].encode('ascii', errors='backslashreplace')))
          mov.appendChild (name)
      
        # IMDB ID: <id> <= <imdburl> with exiting to extract ID
        if kids.nodeName == "imdburl":
          url = kids.childNodes[0].nodeValue
          id = url[url.find("/tt")+1:]
          #print "id:", id
          m['id'] = id
          name = doc.createElement("id")
          name.appendChild (doc.createTextNode(m ['id'].encode('ascii', errors='backslashreplace')))
          mov.appendChild (name)

        # Movie Studio: <studio> <= <studio><displayname>  
        if kids.nodeName == "studios":
          for r in kids.childNodes:
            if r.nodeName == "studio":
              for s in r.childNodes:
                if s.nodeName == "displayname":
                  m['studio'] = s.childNodes[0].nodeValue
                  name = doc.createElement("studio")
                  name.appendChild (doc.createTextNode(m ['studio'].encode('ascii', errors='backslashreplace')))
                  mov.appendChild (name)
      
        # Release Date: <year> <= <releasedate><year>
        if kids.nodeName == "releasedate":
          for r in kids.childNodes:
            if r.nodeName == "year":
              for s in r.childNodes:
                if s.nodeName == "displayname":
                  name = doc.createElement("year")
                  name.appendChild (doc.createTextNode(s.childNodes[0].nodeValue.encode('ascii', errors='backslashreplace')))
                  mov.appendChild (name)


        # Date Added: <dateadded> <= <lastmodified><date> with adjustment for date format.
        # Not a 1:1 translation but close enogh.
        if kids.nodeName == "lastmodified":
          for r in kids.childNodes:
            if r.nodeName == "date":
              name = doc.createElement("dateadded")
              d = r.childNodes[0].nodeValue.encode('ascii', errors='backslashreplace')
              d = d[6:10] + "-" + d[3:5] + "-" + d[0:2] + " " + d[11:]
              name.appendChild (doc.createTextNode(d))
              mov.appendChild (name)

        # Seen/Play Count: <playcount> <= <seenit> with translation of Y/N to 1/0 Play Count
        if kids.nodeName == "seenit":
          name = doc.createElement("playcount")
          if kids.childNodes[0].nodeValue.encode('ascii', errors='backslashreplace') == "No":
            name.appendChild (doc.createTextNode("0"))
          else:
            name.appendChild (doc.createTextNode("1"))
          mov.appendChild (name)
      
        # Genre: <genre> <= <genres><genre><displayname> with multiple entries permitted
        if kids.nodeName == "genres":
          for r in kids.childNodes:
            #print "studios", r.nodeName
            if r.nodeName == "genre":
              for s in r.childNodes:
                if s.nodeName == "displayname":
                  #m['studio'] = s.childNodes[0].nodeValue
                  #print m['studio']
                  name = doc.createElement("genre")
                  name.appendChild (doc.createTextNode(s.childNodes[0].nodeValue.encode('ascii', errors='backslashreplace')))
                  mov.appendChild (name)

        # Tag: ... <tags><tag><displayname>
        # IGNORE
        #if kids.nodeName == "tags":
        #  for r in kids.childNodes:
        #    #print "studios", r.nodeName
        #    if r.nodeName == "tag":
        #      for s in r.childNodes:
        #        if s.nodeName == "displayname":
        #          if s.childNodes[0].nodeValue == "TV Series":
        #            print "TV Show", m['title']
        #          #m['studio'] = s.childNodes[0].nodeValue
        #          #print m['studio']
        #          #name = doc.createElement("genre")
        #          #name.appendChild (doc.createTextNode(s.childNodes[0].nodeValue.encode('ascii', errors='backslashreplace')))
        #          #mov.appendChild (name)

        # Writer/Director Crew: 
        #	<director> <= <crew><crewmember><person><displayname> 
        #	<writer> <= <crew><crewmember><person><displayname>
        if kids.nodeName == "crew":
          for r in kids.childNodes:
            if r.nodeName == "crewmember":
              crew = {}
              crew ['roleid'] = ""
              crew ['displayname'] = ""
              crew ['imageurl'] = ""
              for s in r.childNodes:
                if s.nodeName == "roleid":
                  crew ['roleid'] = s.childNodes[0].nodeValue
                if s.nodeName == "person":
                  for t in s.childNodes:
                    if t.nodeName == "displayname":
                      crew ['displayname'] = t.childNodes[0].nodeValue
              if crew ['roleid'] == "dfDirector":
                name = doc.createElement("director")
                name.appendChild (doc.createTextNode(crew ['displayname'].encode('ascii', errors='backslashreplace')))
                mov.appendChild (name)

              if crew ['roleid'] == "dfWriter":
                name = doc.createElement("credits")
                name.appendChild (doc.createTextNode(crew ['displayname'].encode('ascii', errors='backslashreplace')))
                mov.appendChild (name)
              
        # Cast/Stars: <actor> <= <cast><person><displayname> and more.
        if kids.nodeName == "cast":
            #print "cast"
            cast = {}
            cast ['roleid'] = ""
            cast ['displayname'] = ""
            cast ['imageurl'] = ""
            cast ['role'] = ""
            for r in kids.childNodes:
              for s in r.childNodes:
                if s.nodeName == "roleid":
                  cast ['roleid'] = s.childNodes[0].nodeValue
                if s.nodeName == "character":
                  cast ['role'] = s.childNodes[0].nodeValue  
                if s.nodeName == "person":
                  for t in s.childNodes:
                    if t.nodeName == "displayname":
                      cast ['displayname'] = t.childNodes[0].nodeValue
                    if t.nodeName == "imageurl":
                      cast ['imageurl'] = t.childNodes[0].nodeValue
              if cast ['roleid'] == "dfActor":
                name = doc.createElement("actor")
                detail = doc.createElement("name")
                detail.appendChild (doc.createTextNode(cast ['displayname'].encode('ascii', errors='backslashreplace')))
                name.appendChild (detail)
                detail = doc.createElement("role")
                detail.appendChild (doc.createTextNode(cast ['role'].encode('ascii', errors='backslashreplace')))
                name.appendChild (detail)
                detail = doc.createElement("thumb")
                detail.appendChild (doc.createTextNode(cast ['imageurl'].encode('ascii', errors='backslashreplace')))
                name.appendChild (detail)
                mov.appendChild (name)


        # Links for Trailer and Movie - Complex transformations
        if kids.nodeName == "links":
          for r in kids.childNodes:
            if r.nodeName == "link":
              link = {}
              link ['description'] = ""
              link ['url'] = ""
              link ['urltype'] = ""
              for s in r.childNodes:
                if s.nodeName == "urltype":
                  link ['urltype'] = s.childNodes[0].nodeValue
                if s.nodeName == "url":
                  link ['url'] = s.childNodes[0].nodeValue
                if s.nodeName == "description":
                  link ['description'] = s.childNodes[0].nodeValue
              #print link
              if link ['urltype'] == "Trailer URL":
                m ['trailer'] = "plugin://plugin.video.youtube/?action=play_video&videoid=" + link ['url'][link ['url'].find ("?v=")+3:]
                name = doc.createElement("trailer")
                name.appendChild (doc.createTextNode(m ['trailer'].encode('ascii', errors='backslashreplace')))
                mov.appendChild (name)
              if link ['urltype'] == "Movie":
                m ['path'] = link ['url'][:link ['url'].rfind("/")+1]
                m ['filenameandpath'] = link ['url']
                m ['basepath'] = link ['url']

        # Movie Thumbnail: <thumb> <= <thumbnailpath>        
        if kids.nodeName == "thumbfilepath":
          for r in kids.childNodes:
            m['thumbnail'] = r.nodeValue #kids.childNodes[0].nodeValue

        # Original Title. Save and possibly use it later.
        if kids.nodeName == "originaltitle":
          m['originaltitle'] = kids.childNodes[0].nodeValue

        # Episode Count. For movies, this will be 0...
        if kids.nodeName == "episodecount":
          m['episodecount'] = kids.childNodes[0].nodeValue


      # originaltitle: <originaltitle> <= <originaltitle> or <title>
      if len(m['originaltitle']) == 0:
          m['originaltitle'] = m['title']
      name = doc.createElement("originaltitle")
      name.appendChild (doc.createTextNode(m ['originaltitle'].encode('ascii', errors='backslashreplace')))
      mov.appendChild (name)

      name = doc.createElement("mpaa")
      name.appendChild (doc.createTextNode(m ['mpaa'].encode('ascii', errors='backslashreplace')))
      mov.appendChild (name)




      name = doc.createElement("file")
      name.appendChild (doc.createTextNode(""))
      mov.appendChild (name)

      name = doc.createElement("path")
      name.appendChild (doc.createTextNode(m ['path']))
      mov.appendChild (name)

      name = doc.createElement("filenameandpath")
      name.appendChild (doc.createTextNode(m ['filenameandpath']))
      mov.appendChild (name)

      name = doc.createElement("basepath")
      name.appendChild (doc.createTextNode(m ['basepath']))
      mov.appendChild (name)




      # At the moment, all the images are being copied to a single images directory in the MOVIES
      # folder. This is not ideal, but suits our purposes. It allows us to use the PYTHON web server
      # to serve the images. The code to copy and link has been changed. The old copy code is: 
      #		shutil.copyfile (m['thumbnail'], m['path'] + short)
      #		shutil.copyfile (m['thumbnail'], m['path'] + "images/" + fanart)
      # There are two links to each file. I am not sure which one is used - things seem to work best with
      # both included.
      

      #print m['thumbnail']
      #print m['backgroundbackdrop']      

      if m['coverfront'] != "":
        #poster = m['thumbnail'][m['thumbnail'].rindex("/")+1:]
        fromfn = fixfilename (m['coverfront'])
        #if len(imagesDir) > 0:
        #  myCopy (fromfn, imagesDir + poster)

        # -poster.jpg
        posterJPG = m ['filenameandpath'][:-4] + "-poster.jpg"
        myCopy (fromfn, posterJPG)

        fanart = ""  
        if m['backgroundbackdrop'] != "":
          fromfn = fixfilename (m['backgroundbackdrop'])
          fanart = m['backgroundbackdrop'][m['backgroundbackdrop'].rindex("/")+1:]
          if len(imagesDir) > 0:
            myCopy (fromfn, imagesDir + fanart)          
          
          # -fanart.jpg
          #location = m['thumbnail'][:m['thumbnail'].rindex("/")]
          fanartJPG = m ['filenameandpath'][:-4] + "-fanart.jpg"
          myCopy (fromfn, fanartJPG)

        if server != "":
          name = doc.createElement("thumb")
          name.attributes['aspect'] = "poster"
          name.attributes['preview'] =  server + poster
          name.appendChild (doc.createTextNode( server + poster)) # m ['thumbnail'].encode('ascii', errors='backslashreplace')))
          mov.appendChild (name)

        if fanart != "":
          if server != "":
            fa = doc.createElement ("fanart")
            name = doc.createElement("thumb")
            name.attributes['aspect'] = "poster"
            name.attributes['preview'] = server + fanart
            name.appendChild (doc.createTextNode( server + fanart)) # m ['thumbnail'].encode('ascii', errors='backslashreplace')))
            fa.appendChild (name)
            mov.appendChild (fa)



        if server != "":        
          art = doc.createElement("art")
          thumb = doc.createElement("poster")
          thumb.appendChild (doc.createTextNode( server + poster)) # m ['thumbnail'].encode('ascii', errors='backslashreplace')))
          art.appendChild(thumb)

        if fanart != "":
          if server != "":
            thumb = doc.createElement("fanart")
            thumb.appendChild (doc.createTextNode( server + fanart)) # m ['thumbnail'].encode('ascii', errors='backslashreplace')))
            art.appendChild(thumb)
            mov.appendChild (art)


      if int(m ['episodecount']) == 0:
        movieCount = movieCount + 1

      if m ['filenameandpath'] != "":
        nfo = m ['filenameandpath'][:-3] + "nfo"
        if nfo[:14] == "/Volumes/Media":
          #print nfo

          fh = open (nfo, "wb")
          fh.write (mov.toprettyxml())
          fh.close

          savedFiles = savedFiles + 1
      else:
        if int(m ['episodecount']) == 0:
          if m['format'] == "DVD":
            if m['collectionstatus'] != 'Wanted':
              print "Movie: Not Found:", m ['title']
        


      #outLevel1.appendChild (mov)
      




def processTV(movie):

      global savedFiles
      global movieCount


      verbose = False
      eps = []
      allcrew = []
      allcast = []
      alllink = []
      genres = []

      movielink = ""

      m = {}
      m['originaltitle'] = ""
      m['title'] = ""
      m['plot'] = ""
      m['runtime'] = ""
      m['mpaa'] = "NR"
      m['rating'] = ""
      m['id'] = ""
      m['playcount'] = "0"
      m['trailer'] = ""
      m['studio'] = ""
      m['url'] = ""
      m['year'] = ""
      m['path'] = ""
      m['country'] = ""
      m['coverfront'] = ""
      m['filenameandpath'] = ""
      m['basepath'] = ""
      m['thumbnail'] = ""
      m['episodecount'] = 0
      m['format'] = ""
      m['collectionstatus'] = ""
      m['backgroundbackdrop'] = ''
      m['series'] = ""
      
      #print movie.nodeName

      for kids in movie.childNodes:
        if kids.nodeName == "title": 			# title: <title> <= <title>
          m['title'] = kids.childNodes[0].nodeValue.encode('ascii', errors='backslashreplace')
        if m['title'][:8] == "Top Gear":
          verbose = False
        if kids.nodeName == "plot":			# Movie Plot: <plot> <= <plot>
          m['plot'] = kids.childNodes[0].nodeValue
        if kids.nodeName == "runtime": 			# Run Time - In Minutes: <runtime> <= <runtime>
          m['runtime'] = kids.childNodes[0].nodeValue
        if kids.nodeName == "collectionstatus":		# collectionstatus: <> <= <collectionstatus>
          m['collectionstatus'] = kids.childNodes[0].nodeValue
        if kids.nodeName == "backgroundbackdrop":	# background image: <> <= <backgroundbackdrop>
          m['backgroundbackdrop'] = kids.childNodes[0].nodeValue
        if kids.nodeName == "coverfront":
          m['coverfront'] = kids.childNodes[0].nodeValue
          #print m['coverfront']
        if kids.nodeName == "mpaarating":		# MPAA Rating: <mpaa> <= <mpaarating><displayname
          for r in kids.childNodes:
            if r.nodeName == "displayname":
              m['mpaa'] = r.childNodes[0].nodeValue
        if kids.nodeName == "series":		
          for r in kids.childNodes:
            if r.nodeName == "displayname":
              m['series'] = r.childNodes[0].nodeValue
        if kids.nodeName == "format":			# Media Format: <> <= <format><displayname> - For Info only
          for r in kids.childNodes:
            if r.nodeName == "displayname":
              m['format'] = r.childNodes[0].nodeValue
        if kids.nodeName == "country":			# Country: <country> <= <country><displayname>
          for r in kids.childNodes:
            if r.nodeName == "displayname":
              m['country'] = r.childNodes[0].nodeValue
        if kids.nodeName == "imdbrating":		# IMDB Rating: <rating> <= <imdbrating
          m['rating'] = kids.childNodes[0].nodeValue
        if kids.nodeName == "imdburl":			# IMDB ID: <id> <= <imdburl> with exiting to extract ID
          url = kids.childNodes[0].nodeValue
          id = url[url.find("/tt")+1:]
          m['id'] = id
        if kids.nodeName == "studios":			# Movie Studio: <studio> <= <studio><displayname>
          for r in kids.childNodes:
            if r.nodeName == "studio":
              for s in r.childNodes:
                if s.nodeName == "displayname":
                  m['studio'] = s.childNodes[0].nodeValue
        if kids.nodeName == "releasedate":		# Release Date: <year> <= <releasedate><year>
          for r in kids.childNodes:
            if r.nodeName == "year":
              for s in r.childNodes:
                if s.nodeName == "displayname":
                  m['year'] = s.childNodes[0].nodeValue
        if kids.nodeName == "lastmodified":		# Date Added: <dateadded> <= <lastmodified><date> with adjustment for date format.
          for r in kids.childNodes:
            if r.nodeName == "date":
              d = r.childNodes[0].nodeValue.encode('ascii', errors='backslashreplace')
              m['date'] = d[6:10] + "-" + d[3:5] + "-" + d[0:2] + " " + d[11:]
        if kids.nodeName == "seenit":			# Seen/Play Count: <playcount> <= <seenit> with translation of Y/N to 1/0 Play Coun
          if kids.childNodes[0].nodeValue.encode('ascii', errors='backslashreplace') == "No":
            m['playcount'] = "0"
          else:
            m['playcount'] = "1"
        if kids.nodeName == "thumbfilepath":			# Movie Thumbnail: <thumb> <= <thumbnailpath>
          for r in kids.childNodes:
            m['thumbnail'] = r.nodeValue #kids.childNodes[0].nodeValue
        if kids.nodeName == "originaltitle":			# Original Title. Save and possibly use it later.
          m['originaltitle'] = kids.childNodes[0].nodeValue
        if kids.nodeName == "episodecount":			# Episode Count. For movies, this will be 0...
          m['episodecount'] = kids.childNodes[0].nodeValue
        if kids.nodeName == "genres":			# Genre: <genre> <= <genres><genre><displayname> with multiple entries permitted
          for r in kids.childNodes:
            if r.nodeName == "genre":
              for s in r.childNodes:
                if s.nodeName == "displayname":
                  genres.append (s.childNodes[0].nodeValue)


        # Writer/Director Crew: 
        #	<director> <= <crew><crewmember><person><displayname> 
        #	<writer> <= <crew><crewmember><person><displayname>
        if kids.nodeName == "crew":
          for r in kids.childNodes:
            if r.nodeName == "crewmember":
              crew = {}
              crew ['roleid'] = ""
              crew ['displayname'] = ""
              crew ['imageurl'] = ""
              for s in r.childNodes:
                if s.nodeName == "roleid":
                  crew ['roleid'] = s.childNodes[0].nodeValue
                if s.nodeName == "person":
                  for t in s.childNodes:
                    if t.nodeName == "displayname":
                      crew ['displayname'] = t.childNodes[0].nodeValue
              allcrew.append (crew)
              
              
        # Cast/Stars: <actor> <= <cast><person><displayname> and more.
        if kids.nodeName == "cast":
            #print "cast"
            for r in kids.childNodes:
              cast = {}
              cast ['roleid'] = ""
              cast ['displayname'] = ""
              cast ['imageurl'] = ""
              cast ['role'] = ""
              for s in r.childNodes:
                if s.nodeName == "roleid":
                  cast ['roleid'] = s.childNodes[0].nodeValue
                if s.nodeName == "character":
                  cast ['role'] = s.childNodes[0].nodeValue  
                if s.nodeName == "person":
                  for t in s.childNodes:
                    if t.nodeName == "displayname":
                      cast ['displayname'] = t.childNodes[0].nodeValue
                    if t.nodeName == "imageurl":
                      cast ['imageurl'] = t.childNodes[0].nodeValue
              if cast ['roleid'] == "dfActor":
                allcast.append (cast)
                


        # Links for Trailer and Movie - Complex transformations
        if kids.nodeName == "links":
          for r in kids.childNodes:
            if r.nodeName == "link":
              link = {}
              link ['description'] = ""
              link ['url'] = ""
              link ['urltype'] = ""
              for s in r.childNodes:
                if s.nodeName == "urltype":
                  link ['urltype'] = s.childNodes[0].nodeValue
                if s.nodeName == "url":
                  link ['url'] = s.childNodes[0].nodeValue
                if s.nodeName == "description":
                  link ['description'] = s.childNodes[0].nodeValue
              alllink.append (link)
              






        if kids.nodeName == "discs":
          for r in kids.childNodes: 
            if r.nodeName == "disc":
              for s in r.childNodes:
                if s.nodeName == "episodes":
                  for t in s.childNodes:
                    if t.nodeName == "episode":
                      n = {}
                      n['title'] = ""
                      n['plot'] = ""
                      n['runtime'] = ""
                      n['movielink'] = ""
                      n['image'] = ""
                      n['firstairdate'] = ""
                      air_year = ""
                      air_month = ""
                      air_day = ""
                      for u in t.childNodes:
                        if u.nodeName == "title":
                          n['title'] = u.childNodes[0].nodeValue
                        if u.nodeName == "plot":
                          n['plot'] = u.childNodes[0].nodeValue                               
                        if u.nodeName == "runtime":
                          n['runtime'] = u.childNodes[0].nodeValue                               
                        if u.nodeName == "movielink":
                          n['movielink'] = u.childNodes[0].nodeValue                               
                          movielink = n['movielink']
                          if verbose == True:
                            print movielink
                        if u.nodeName == "firstairdate":
                          for v in u.childNodes:
                            if v.nodeName == "day":
                              air_day = v.childNodes[0].nodeValue
                            if v.nodeName == "month":
                              air_month = v.childNodes[0].nodeValue
                            if v.nodeName == "year":
                              air_year = v.childNodes[0].childNodes[0].nodeValue
                            #if v.nodeName == "date":
                            #  n['firstairdate'] = v.childNodes[0].nodeValue
                            #print air_year
                            #print air_month
                            #print air_day
                            n['firstairdate'] = air_year + "-" + air_month + "-" + air_day
                        #if u.nodeName == "image":
                        #  n['image'] = u.childNodes[0].nodeValue                               
                        if u.nodeName == "largeimage":
                          n['image'] = u.childNodes[0].nodeValue                               
                      eps.append (n)            
                      if verbose: 
                        print n['title'], " ", n['movielink']
                      if n['movielink'] != "":
                        movielink = n['movielink']




      if True:	# Create tvshow.nfo
        doc = Document()
        name = doc.createElement("version")
        name.appendChild (doc.createTextNode("1"))
        mov = doc.createElement("tvshow")

        name = doc.createElement("dateadded")
        name.appendChild (doc.createTextNode(m['date']))
        mov.appendChild (name)

        name = doc.createElement("mpaa")
        name.appendChild (doc.createTextNode(m ['mpaa'].encode('ascii', errors='backslashreplace')))
        mov.appendChild (name)

        name = doc.createElement("plot")
        name.appendChild (doc.createTextNode(m ['plot'].encode('ascii', errors='backslashreplace')))
        mov.appendChild (name)

        name = doc.createElement("runtime")
        name.appendChild (doc.createTextNode(m ['runtime'].encode('ascii', errors='backslashreplace')))
        mov.appendChild (name)

        name = doc.createElement("rating")
        name.appendChild (doc.createTextNode(m ['rating'].encode('ascii', errors='backslashreplace')))
        mov.appendChild (name)

        name = doc.createElement("country")
        name.appendChild (doc.createTextNode(m['country'].encode('ascii', errors='backslashreplace')))
        mov.appendChild (name)

        name = doc.createElement("id")
        name.appendChild (doc.createTextNode(m ['id'].encode('ascii', errors='backslashreplace')))
        mov.appendChild (name)

        name = doc.createElement("studio")
        name.appendChild (doc.createTextNode(m ['studio'].encode('ascii', errors='backslashreplace')))
        mov.appendChild (name)

        if m['year'] == "":
          print "TV: No Year:", m['title']
        name = doc.createElement("year")
        name.appendChild (doc.createTextNode(m['year'].encode('ascii', errors='backslashreplace')))
        mov.appendChild (name)

        name = doc.createElement("playcount")          
        name.appendChild (doc.createTextNode(m['playcount']))
        mov.appendChild (name)


        # originaltitle: <originaltitle> <= <originaltitle> or <title>
        #if len(m['originaltitle']) == 0:
        #  m['originaltitle'] = m['title']
          
        #name = doc.createElement("originaltitle")
        #name.appendChild (doc.createTextNode(m ['originaltitle'].encode('ascii', errors='backslashreplace')))
        #mov.appendChild (name)

        name = doc.createElement("title")
        name.appendChild (doc.createTextNode(m ['series'].encode('ascii', errors='backslashreplace')))
        mov.appendChild (name)

        name = doc.createElement("showtitle")
        name.appendChild (doc.createTextNode(m ['series'].encode('ascii', errors='backslashreplace')))
        mov.appendChild (name)

        #name = doc.createElement("file")
        #name.appendChild (doc.createTextNode(""))
        #mov.appendChild (name)

        #name = doc.createElement("path")
        #name.appendChild (doc.createTextNode(m ['path']))
        #mov.appendChild (name)

        #name = doc.createElement("filenameandpath")
        #name.appendChild (doc.createTextNode(m ['filenameandpath']))
        #mov.appendChild (name)

        #name = doc.createElement("basepath")
        #name.appendChild (doc.createTextNode(m ['basepath']))
        #mov.appendChild (name)

        for mycrew in allcrew:
          if mycrew ['roleid'] == "dfDirector":
            name = doc.createElement("director")
            name.appendChild (doc.createTextNode(mycrew ['displayname'].encode('ascii', errors='backslashreplace')))
            mov.appendChild (name)
          if mycrew ['roleid'] == "dfWriter":
            name = doc.createElement("credits")
            name.appendChild (doc.createTextNode(mycrew ['displayname'].encode('ascii', errors='backslashreplace')))
            mov.appendChild (name)
          for genre in genres:                  
            name = doc.createElement("genre")
            name.appendChild (doc.createTextNode(genre.encode('ascii', errors='backslashreplace')))
            mov.appendChild (name)

        for cast in allcast:
          name = doc.createElement("actor")
          detail = doc.createElement("name")
          detail.appendChild (doc.createTextNode(cast ['displayname'].encode('ascii', errors='backslashreplace')))
          name.appendChild (detail)
          detail = doc.createElement("role")
          detail.appendChild (doc.createTextNode(cast ['role'].encode('ascii', errors='backslashreplace')))
          name.appendChild (detail)
          detail = doc.createElement("thumb")
          detail.appendChild (doc.createTextNode(cast ['imageurl'].encode('ascii', errors='backslashreplace')))
          name.appendChild (detail)
          mov.appendChild (name)


        for link in alllink:
          #print link
          if link ['urltype'] == "Trailer URL":
            m ['trailer'] = "plugin://plugin.video.youtube/?action=play_video&videoid=" + link ['url'][link ['url'].find ("?v=")+3:]
            name = doc.createElement("trailer")
            name.appendChild (doc.createTextNode(m ['trailer'].encode('ascii', errors='backslashreplace')))
            mov.appendChild (name)
          if link ['urltype'] == "Movie":
            print "NOT IMPLEMENTED!:"


      # At the moment, all the images are being copied to a single images directory in the MOVIES
      # folder. This is not ideal, but suits our purposes. It allows us to use the PYTHON web server
      # to serve the images. The code to copy and link has been changed. The old copy code is: 
      #		shutil.copyfile (m['thumbnail'], m['path'] + short)
      #		shutil.copyfile (m['thumbnail'], m['path'] + "images/" + fanart)
      # There are two links to each file. I am not sure which one is used - things seem to work best with
      # both included.
      
      

        #if m['thumbnail'] != "":
        #  poster = m['thumbnail'][m['thumbnail'].rindex("/")+1:]
        #  if not os.path.isfile (imagesDir + poster):
        #    shutil.copyfile (m['thumbnail'], imagesDir + poster)
        #
        #  fanart = ""  
        #  if m['backgroundbackdrop'] != "":
        #    fanart = m['backgroundbackdrop'][m['backgroundbackdrop'].rindex("/")+1:]
        #    if not os.path.isfile (imagesDir + fanart):
        #      shutil.copyfile (m['thumbnail'], imagesDir + fanart)          
          










        if m['coverfront'] != "":
          #poster = m['thumbnail'][m['thumbnail'].rindex("/")+1:]
          fromfn = fixfilename (m['coverfront'])
          #if len(imagesDir) > 0:
          #  myCopy (fromfn, imagesDir + poster)

          # -poster.jpg
          posterJPG = m ['filenameandpath'][:-4] + "-poster.jpg"
          myCopy (fromfn, posterJPG)

          fanart = ""
          if m['backgroundbackdrop'] != "":
            fromfn = fixfilename (m['backgroundbackdrop'])
            fanart = m['backgroundbackdrop'][m['backgroundbackdrop'].rindex("/")+1:]
            if len(imagesDir) > 0:
              myCopy (fromfn, imagesDir + fanart)

            # -fanart.jpg
            #location = m['thumbnail'][:m['thumbnail'].rindex("/")]
            fanartJPG = m ['filenameandpath'][:-4] + "-fanart.jpg"
            myCopy (fromfn, fanartJPG)









          if server != "":
            name = doc.createElement("thumb")
            name.attributes['aspect'] = "poster"
            name.attributes['preview'] = server + poster
            name.appendChild (doc.createTextNode( server + poster)) # m ['thumbnail'].encode('ascii', errors='backslashreplace')))
            mov.appendChild (name)

          if fanart != "":
            if server != "":
              fa = doc.createElement ("fanart")
              name = doc.createElement("thumb")
              name.attributes['aspect'] = "poster"
              name.attributes['preview'] = server + fanart
              name.appendChild (doc.createTextNode( server + fanart)) # m ['thumbnail'].encode('ascii', errors='backslashreplace')))
              fa.appendChild (name)
              mov.appendChild (fa)

        
          if server != "":
            art = doc.createElement("art")
            thumb = doc.createElement("poster")
            thumb.appendChild (doc.createTextNode( server + poster)) # m ['thumbnail'].encode('ascii', errors='backslashreplace')))
            art.appendChild(thumb)

          if fanart != "":
            if server != "":
              thumb = doc.createElement("fanart")
              thumb.appendChild (doc.createTextNode( server + fanart)) # m ['thumbnail'].encode('ascii', errors='backslashreplace')))
              art.appendChild(thumb)
              mov.appendChild (art)



        if m ['filenameandpath'] != "":
          nfo = m ['filenameandpath'][:-3] + "nfo"
          if nfo[:14] == "/Volumes/Media":
            #print nfo

            fh = open (nfo, "wb")
            fh.write (mov.toprettyxml())
            fh.close

            savedFiles = savedFiles + 1
        else:
          if int(m ['episodecount']) == 0:
            if m['format'] == "DVD":
              if m['collectionstatus'] != 'Wanted':
                print "Movie Not Found", m ['title']
        
        if movielink != "":        
          nfo = movielink[:movielink.rindex("/")+1] + "tvshow.nfo"
          if verbose:
            print nfo
          fh = open (nfo, "wb")
          fh.write (mov.toprettyxml())
          fh.close
        
        

        #print "ML:", movielink, m['thumbnail']
        if m['coverfront'] != "" and movielink != "":
          folderjpg = movielink[:movielink.rindex("/")+1] + "folder.jpg"
          fromfn = fixfilename (m['coverfront'])
          if not os.path.isfile (folderjpg):
            print "More Cache", fromfn, folderjpg, movielink
            myCopy (fromfn, folderjpg)
                        
            
                    

      #outLevel1.appendChild (mov)
      

        ##########################
        # Individual files
      
      
      for ep in eps:
      
        doc = Document()
        name = doc.createElement("version")
        name.appendChild (doc.createTextNode("1"))
        mov = doc.createElement("episodedetails")

        name = doc.createElement("dateadded")
        name.appendChild (doc.createTextNode(m['date']))
        mov.appendChild (name)

        name = doc.createElement("aired")
        if ep['firstairdate'] != "":
          name.appendChild (doc.createTextNode(ep['firstairdate'].encode('ascii', errors='backslashreplace')))
        else:
          name.appendChild (doc.createTextNode(m['year']))
        mov.appendChild (name)

        #name = doc.createElement("dateadded")
        #name.appendChild (doc.createTextNode(m['date']))
        #mov.appendChild (name)
        
        

        name = doc.createElement("season")
        name.appendChild (doc.createTextNode("-1".encode('ascii', errors='backslashreplace')))
        mov.appendChild (name)

        name = doc.createElement("episode")
        name.appendChild (doc.createTextNode("-1".encode('ascii', errors='backslashreplace')))
        mov.appendChild (name)


        name = doc.createElement("showtitle")
        name.appendChild (doc.createTextNode(m ['series'].encode('ascii', errors='backslashreplace')))
        mov.appendChild (name)


        name = doc.createElement("mpaa")
        name.appendChild (doc.createTextNode(m ['mpaa'].encode('ascii', errors='backslashreplace')))
        mov.appendChild (name)

        name = doc.createElement("plot")
        name.appendChild (doc.createTextNode(ep ['plot'].encode('ascii', errors='backslashreplace')))
        mov.appendChild (name)

        name = doc.createElement("runtime")
        name.appendChild (doc.createTextNode(ep ['runtime'].encode('ascii', errors='backslashreplace')))
        mov.appendChild (name)

        name = doc.createElement("rating")
        name.appendChild (doc.createTextNode(m ['rating'].encode('ascii', errors='backslashreplace')))
        mov.appendChild (name)

        name = doc.createElement("country")
        name.appendChild (doc.createTextNode(m['country'].encode('ascii', errors='backslashreplace')))
        mov.appendChild (name)

        name = doc.createElement("id")
        name.appendChild (doc.createTextNode(m ['id'].encode('ascii', errors='backslashreplace')))
        mov.appendChild (name)

        name = doc.createElement("studio")
        name.appendChild (doc.createTextNode(m ['studio'].encode('ascii', errors='backslashreplace')))
        mov.appendChild (name)

        name = doc.createElement("year")
        name.appendChild (doc.createTextNode(m['year'].encode('ascii', errors='backslashreplace')))
        mov.appendChild (name)

        name = doc.createElement("playcount")          
        name.appendChild (doc.createTextNode(m['playcount']))
        mov.appendChild (name)


        # originaltitle: <originaltitle> <= <originaltitle> or <title>
        #if len(m['originaltitle']) == 0:
        #  m['originaltitle'] = m['title']
          
        #name = doc.createElement("originaltitle")
        #name.appendChild (doc.createTextNode(m ['originaltitle'].encode('ascii', errors='backslashreplace')))
        #mov.appendChild (name)

        name = doc.createElement("title")
        name.appendChild (doc.createTextNode(ep ['title'].encode('ascii', errors='backslashreplace')))
        mov.appendChild (name)

        #name = doc.createElement("file")
        #name.appendChild (doc.createTextNode(""))
        #mov.appendChild (name)

        #name = doc.createElement("path")
        #name.appendChild (doc.createTextNode(m ['path']))
        #mov.appendChild (name)

        #name = doc.createElement("filenameandpath")
        #name.appendChild (doc.createTextNode(m ['filenameandpath']))
        #mov.appendChild (name)

        #name = doc.createElement("basepath")
        #name.appendChild (doc.createTextNode(m ['basepath']))
        #mov.appendChild (name)

        for mycrew in allcrew:
          if mycrew ['roleid'] == "dfDirector":
            name = doc.createElement("director")
            name.appendChild (doc.createTextNode(mycrew ['displayname'].encode('ascii', errors='backslashreplace')))
            mov.appendChild (name)
          if mycrew ['roleid'] == "dfWriter":
            name = doc.createElement("credits")
            name.appendChild (doc.createTextNode(mycrew ['displayname'].encode('ascii', errors='backslashreplace')))
            mov.appendChild (name)
          for genre in genres:                  
            name = doc.createElement("genre")
            name.appendChild (doc.createTextNode(genre.encode('ascii', errors='backslashreplace')))
            mov.appendChild (name)

        for cast in allcast:
          name = doc.createElement("actor")
          detail = doc.createElement("name")
          detail.appendChild (doc.createTextNode(cast ['displayname'].encode('ascii', errors='backslashreplace')))
          name.appendChild (detail)
          detail = doc.createElement("role")
          detail.appendChild (doc.createTextNode(cast ['role'].encode('ascii', errors='backslashreplace')))
          name.appendChild (detail)
          detail = doc.createElement("thumb")
          detail.appendChild (doc.createTextNode(cast ['imageurl'].encode('ascii', errors='backslashreplace')))
          name.appendChild (detail)
          mov.appendChild (name)


        for link in alllink:
          #print link
          if link ['urltype'] == "Trailer URL":
            m ['trailer'] = "plugin://plugin.video.youtube/?action=play_video&videoid=" + link ['url'][link ['url'].find ("?v=")+3:]
            name = doc.createElement("trailer")
            name.appendChild (doc.createTextNode(m ['trailer'].encode('ascii', errors='backslashreplace')))
            mov.appendChild (name)
          if link ['urltype'] == "Movie":
            print "NOT IMPLEMENTED!:"


      # At the moment, all the images are being copied to a single images directory in the MOVIES
      # folder. This is not ideal, but suits our purposes. It allows us to use the PYTHON web server
      # to serve the images. The code to copy and link has been changed. The old copy code is: 
      #		shutil.copyfile (m['thumbnail'], m['path'] + short)
      #		shutil.copyfile (m['thumbnail'], m['path'] + "images/" + fanart)
      # There are two links to each file. I am not sure which one is used - things seem to work best with
      # both included.
      
      

        if ep['image'] != "":
          #poster = ep['image'][ep['image'].rindex("/")+1:]
          #if not os.path.isfile (imagesDir + poster):
          #  shutil.copyfile (ep['image'], imagesDir + poster)
        
          fanart = ""  
          if m['backgroundbackdrop'] != "":
            fanart = m['backgroundbackdrop'][m['backgroundbackdrop'].rindex("/")+1:]
            if len(imagesDir) > 0:
              myCopy (m['thumbnail'], imagesDir + fanart)          


          image = ep['image']
          if image[:4] == "http":
            



            if ep ['movielink'] != "":
              # This is the thumbnail in the same directory...
              jpg = ep ['movielink'][:-4] + "-thumb.jpg"
              if not os.path.isfile(jpg):
                print "TV: Downloading Cache: ",  jpg      
                f = open(jpg,'wb')
                f.write(urllib.urlopen(image).read())
                f.close()
            
            
            if len(imagesDir) > 0:
              if not os.path.isfile (imagesDir + "eps_" + ep['image'][ep['image'].rindex("/")+1:]):
                print "TV: Downloading Cache: ",  "eps_" + ep['image'][ep['image'].rindex("/")+1:], image      
                f = open(imagesDir + "eps_" + ep['image'][ep['image'].rindex("/")+1:],'wb')
                f.write(urllib.urlopen(image).read())
                f.close()
            image = "eps_" + ep['image'][ep['image'].rindex("/")+1:] 
            

          if server != "":
            name = doc.createElement("thumb")
            name.attributes['aspect'] = "poster"
            name.attributes['preview'] =  server + image
            name.appendChild (doc.createTextNode( server + image)) # m ['thumbnail'].encode('ascii', errors='backslashreplace')))
            mov.appendChild (name)

          if fanart != "":
            if server != "":
              fa = doc.createElement ("fanart")
              name = doc.createElement("thumb")
              name.attributes['aspect'] = "poster"
              name.attributes['preview'] = server + fanart
              name.appendChild (doc.createTextNode( server + fanart)) # m ['thumbnail'].encode('ascii', errors='backslashreplace')))
              fa.appendChild (name)
              mov.appendChild (fa)

        
          if server != "":
            art = doc.createElement("art")
            thumb = doc.createElement("poster")
            thumb.appendChild (doc.createTextNode(server + image)) # m ['thumbnail'].encode('ascii', errors='backslashreplace')))
            art.appendChild(thumb)

          if fanart != "":
            if server != "":
              thumb = doc.createElement("fanart")
              thumb.appendChild (doc.createTextNode( server + fanart)) # m ['thumbnail'].encode('ascii', errors='backslashreplace')))
              art.appendChild(thumb) 
              mov.appendChild (art)



        if ep ['movielink'] != "":
          nfo = ep ['movielink'][:-3] + "nfo"
          if nfo[:14] == "/Volumes/Media":
            #print nfo

            fh = open (nfo, "wb")
            fh.write (mov.toprettyxml())
            fh.close

            savedFiles = savedFiles + 1

        #if movielink != "":        
        #  nfo = movielink[:movielink.rindex("/")+1] + "tvshow.nfo"
        #  print nfo
        #  fh = open (nfo, "wb")
        #  fh.write (mov.toprettyxml())
        #  fh.close
        

      #outLevel1.appendChild (mov)


def num (s):
    try:
        return int(s)
    except exceptions.ValueError:
        return 0




def isTV (movie):

      tag = False
      episodeCount = 0
      title = "um"

      for kids in movie.childNodes:
        
        if kids.nodeName == "tags":
          for r in kids.childNodes:
            if r.nodeName == "tag":
              for s in r.childNodes:
                #print s.nodeName
                if s.nodeName == "displayname":
                  if s.childNodes[0].nodeValue == "TV Series":
                    #print "TV Show"
                    tag = True

        if kids.nodeName == "episodecount":
          episodeCount = num(kids.childNodes[0].nodeValue)
          #print kids.childNodes[0].nodeValue
          
        if kids.nodeName == "title":
          title = kids.childNodes[0].nodeValue.encode('ascii', errors='backslashreplace')
          
      #print "Decision"
      if tag == True and episodeCount > 0:
        #print "TV"
        return True
      else:
        #print "Not TV"
        if episodeCount > 1:
          print "Movie: Episodes Found: ", title, " ", episodeCount
        return False











#outLevel1.appendChild (name)



for movieinfonode in xmldoc.getElementsByTagName ("movieinfo"):
 for movieinfonode in xmldoc.getElementsByTagName ("movieinfo"):
  for movies in xmldoc.getElementsByTagName ("movielist"):
    m = {}
    for movie in xmldoc.getElementsByTagName ("movie"):
    
      if isTV(movie):
        processTV(movie)
      else:
        processMovies (movie)
        x = 1

      
      
#mov = doc.createElement("paths")
#outLevel1.appendChild (mov)

print "Saved Files: ", savedFiles, " MovieCount: ", movieCount


#doc.appendChild (outLevel1)
#print doc.toprettyxml()


#fh = open ("test.xml", "wb")
#fh.write (doc.toprettyxml())
#fh.close

exit
