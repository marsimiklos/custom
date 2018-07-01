import re

ADE_BASEURL = 'http://www.adultdvdempire.com'
ADE_SEARCH_MOVIES = ADE_BASEURL + '/dvd/search?q=%s'
ADE_MOVIE_INFO = ADE_BASEURL + '/%s/'

def Start():
  HTTP.CacheTime = CACHE_1DAY
  HTTP.SetHeader('User-agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.2; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0)')

class ADEAgent(Agent.Movies):
  name = 'Custom Add Actor'
  languages = [Locale.Language.English]
  primary_provider = True
  accepts_from = ['com.plexapp.agents.localmedia']
  primary_provider = True


  def search(self, results, media, lang):
    title = media.name
    if media.primary_metadata is not None:
      title = media.primary_metadata.title
      datas = media.name.split(".")
	  studio = datas[0]
	  actors = [] 
	  date = datas[1] + "-" + datas[2] + "-" + datas[3]

    results.Append(MetadataSearchResult(id = media.name, name = "1." + media.name, score = 100, lang = eng))

    results.Sort('score', descending=True)

  def update(self, metadata, media, lang):
    html = HTML.ElementFromURL(ADE_MOVIE_INFO % metadata.id)
    metadata.title = media.title

    # Thumb and Poster
    try:
      img = html.xpath('//*[@id="front-cover"]/img')[0]
      thumbUrl = img.get('src')

      thumb = HTTP.Request(thumbUrl)
      posterUrl = img.get('src')
      metadata.posters[posterUrl] = Proxy.Preview(thumb)
    except:
      pass

    # Tagline
    try: metadata.tagline = html.xpath('//p[@class="Tagline"]')[0].text_content().strip()
    except: pass

    # Summary.
    try:
      for summary in html.xpath('//*[@id="content"]/div[2]/div[2]/div/p'):
        metadata.summary = summary.text_content()
    except Exception, e:
      Log('Got an exception while parsing summary %s' %str(e))

    # Product info div
    data = {}

    productinfo = HTML.StringFromElement(html.xpath('//*[@id="content"]/div[2]/div[4]/div/div[1]/ul')[0])

    productinfo = productinfo.replace('<small>', '|')
    productinfo = productinfo.replace('</small>', '')
    productinfo = productinfo.replace('<li>', '').replace('</li>', '')
    productinfo = HTML.ElementFromString(productinfo).text_content()

    data = media.name.split(".")
	studio = data[0]
	actors = [] 
	orig = data[1] + "-" + data[2] + "-" + data[3]
	actors.append(data[4] + ' ' + data[5])
	if data[6] == 'and':
  		actors.append(data[7] + ' ' + data[8])

    # Rating
    if data.has_key('Rating'):
      metadata.content_rating = 100

    # Studio    
    if data.has_key('Studio'):
      metadata.studio = studio

    # Release   
    if data.has_key('Released'):
      try:
        metadata.originally_available_at = Datetime.ParseDate(orig).date()
        metadata.year = metadata.originally_available_at.year
      except: pass
 	

    try:
      starring = actors
      metadata.roles.clear()
      for member in starring:
        role = metadata.roles.new()
        lename = member.text_content().strip()
        try:
          role.name = lename
        except:
          try:
            role.actor = lename
          except: pass
    except: pass


    # Cast
    try:
      metadata.roles.clear()
      htmlcast = html.xpath('//a[contains(@class, "PerformerName")]')
      for cast in htmlcast:
        cname = cast.text_content().strip()
        if (len(cname) > 0):
          role = metadata.roles.new()
          role.name = cname
    except Exception, e:
      Log('Got an exception while parsing cast %s' %str(e))
