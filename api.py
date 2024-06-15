from flask import Response, jsonify, Flask, request, redirect
import requests
    
class Invidious:

    def generateXML(self, json_data):
        xml_string = '<?xml version=\'1.0\' encoding=\'UTF-8\'?>'
        xml_string += '<feed xmlns:openSearch=\'http://a9.com/-/spec/opensearch/1.1/\' xmlns:media=\'http://search.yahoo.com/mrss/\' xmlns:yt=\'http://www.youtube.com/xml/schemas/2015\'>'
        xml_string += '<title type=\'text\'>Videos</title>'
        xml_string += '<author>'
        xml_string += '<name>Liinback</name>'
        xml_string += '<uri>http://liinback.com</uri>'
        xml_string += '</author>'
        xml_string += '<generator ver=\'1.0\' uri=\'http://kamil.cc/\'>Liinback data API</generator>'
        xml_string += '<openSearch:totalResults>0</openSearch:totalResults>'
        xml_string += '<openSearch:startIndex>1</openSearch:startIndex>'
        xml_string += '<openSearch:itemsPerPage>20</openSearch:itemsPerPage>'

        for item in json_data:
            if 'videoId' not in item:
                continue
        
            xml_string += '<entry>'
            xml_string += '<id>http://127.0.0.1/api/videos/' + self.escape_xml(item['videoId']) + '</id>'
            xml_string += '<published>' + self.escape_xml(item['publishedText']) + '</published>'
            xml_string += '<title type=\'text\'>' + self.escape_xml(item['title']) + '</title>'
            xml_string += '<link rel=\'http://127.0.0.1/api/videos/' + self.escape_xml(item['videoId']) + '/related\'/>'
            xml_string += '<author>'
            xml_string += '<name>' + self.escape_xml(item['author']) + '</name>'
            xml_string += '<uri>http://127.0.0.1/api/channels/' + self.escape_xml(item.get('channel_id', '')) + '</uri>'
            xml_string += '</author>'
            xml_string += '<media:group>'
            xml_string += '<media:thumbnail yt:name=\'hqdefault\' url=\'http://i.ytimg.com/vi/' + self.escape_xml(item['videoId']) + '/hqdefault.jpg\' height=\'240\' width=\'320\' time=\'00:00:00\'/>'
            xml_string += '<yt:duration seconds=\'' + self.escape_xml(str(item['lengthSeconds'])) + '\'/>'
            xml_string += '<yt:videoid id=\'' + self.escape_xml(item['videoId']) + '\'>' + self.escape_xml(item['videoId']) + '</yt:videoid>'
            xml_string += '<media:credit role=\'uploader\' name=\'' + self.escape_xml(item['author']) + '\'>' + self.escape_xml(item['author']) + '</media:credit>'
            xml_string += '</media:group>'
            xml_string += f'<yt:statistics favoriteCount=\'{item["viewCount"]}\' viewCount=\'{item["viewCount"]}\'/>'
            xml_string += '</entry>'

        xml_string += '</feed>'

        return xml_string
        
    def search(self, query):
        response = requests.get('https://vid.puffyan.us/api/v1/search?q={}'.format(query))
        response.raise_for_status()  # Raise an exception for HTTP errors
        json_data = response.json()
        xml_data = self.generateXML(json_data)
        return Response(xml_data, mimetype='text/atom+xml')
    
    def trends(self, type_param=None):
        trends_endpoint = "trending"
        if type_param:
            response = requests.get(f"http://vid.puffyan.us/api/v1/{trends_endpoint}?type={type_param}")
        else:
            response = requests.get(f"http://vid.puffyan.us/api/v1/{trends_endpoint}")

        if response.status_code == 200:
            json_data = response.json()
            xml_data = self.generateXML(json_data)
            return Response(xml_data, mimetype='text/atom+xml')
        else:
            error_message = {"error": "Invalid response format"}
            return jsonify(error_message), 500

    def popular(self):
        popular_endpoint = "popular"
        response = requests.get(f"http://vid.puffyan.us/api/v1/{popular_endpoint}")

        if response.status_code == 200:
            json_data = response.json()
            xml_data = self.generateXML(json_data)
            return Response(xml_data, mimetype='text/atom+xml')
        else:
            error_message = {"error": "Invalid response format"}
            return jsonify(error_message), 500
        
    def user_uploads(self, channel_id=None):
        channels_endpoint = "channels"
        response = requests.get(f"http://vid.puffyan.us/api/v1/{channels_endpoint}/{channel_id}/videos")

        if response.status_code == 200:
            json_data = response.json()
            videos = json_data.get("videos", [])
            xml_data = self.generateXML(videos)
            return Response(xml_data, mimetype='text/atom+xml')
        else:
            error_message = {"error": "Invalid response format"}
            return jsonify(error_message), 500
        
    @staticmethod
    def escape_xml(s):
        if s is None:
            return ''
        return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&apos;')
