import json
from bs4 import BeautifulSoup,Tag
import requests
from ..log import dbMangements as logs
class TagManager(object):
    def __init__(self,tags):
        """판별후 인스턴스 리턴."""
        self.tags = tags   #블로그 컨텐츠 전부
        self.tagMap={"text":{"common":'se-component',
                                 "catches":['se-text']},
                         "horizontalline":{"common":'se-component',
                                 "catches":['se-horizontalLine']},
                         "sticker":{"common":'se-component',
                                 "catches":['se-sticker']},
                         "oembed":{"common":'se-component',
                                      "catches":['se-oembed']},
                         "image":{"common":'se-component',
                                      "catches":['se-imageStrip','se-image']},
                         "oglink":{"common":'se-component',
                                      "catches":['se-oglink']},
                         "video":{"common":'se-component',
                                      "catches":['se-video']},
                         "quotation":{"common":'se-component',
                                      "catches":['se-quotation']},
                         "map":{"common":'se-component',
                                      "catches":['se-placesMap']},
                         "mr_blog":{"common":'se-component',
                                      "catches":['se-mrBlog']},
                         "table":{"common":'se-component',
                                      "catches":['se-table']},
                         "title":{"common":"se-component",
                                        "catches":['se-sectionTitle']}
                         }
        self.separationResult=[]
    def __tagSeparation(self,tag):
        """tag Separation"""
        tag_class=' '.join(tag.attrs['class'])
        for key,sub_dict in self.tagMap.items():
            common=sub_dict["common"]
            catches=sub_dict["catches"]
            if common in tag_class:
                for catch in catches:
                    if catch in tag_class:
                        return key
        return None
    def getInstance(self):
        if self.__tagSeparation(self.tags) == 'text':
            return TextTag
        elif self.__tagSeparation(self.tags)=="horizontalline":
            return HorizontalTag
        elif self.__tagSeparation(self.tags)=="sticker":
            return StickerTag
        elif self.__tagSeparation(self.tags)=="oembed":
            return Oembed
        elif self.__tagSeparation(self.tags)=="image":
            return Image
        elif self.__tagSeparation(self.tags)=="oglink":
            return Oglink
        elif self.__tagSeparation(self.tags)=="video":
            return Video
        elif self.__tagSeparation(self.tags)=="quotation":
            return Quotation
        elif self.__tagSeparation(self.tags)=="map":
            return Map
        elif self.__tagSeparation(self.tags)=="mr_blog":
            return MrBlog
        elif self.__tagSeparation(self.tags)=="table":
            return Table
        elif self.__tagSeparation(self.tags)=="title":
            return Title
        else:
            return None
    def tagReturn(self):
        try:
            instances=self.getInstance()
            if instances is None:
                return {}
            instances=instances(self.tags)
            if instances is not None:
                instances.get_id()
                instances.get_contents()
                diction= instances.resultDiction()
                return diction
            else:
                return {}
        except Exception as err:
            print(err)
            logs.addToMainLogs('', 'ERROR', "tag_managerments.py", str(err).replace('"', '').replace("'", ''))
            return {}
    def parents_tags(self):
        all_div_parents=list(filter(lambda x:isinstance(x,Tag),self.tags.contents))
        for parent in all_div_parents:
            parents_dict = {}
            key=self.__tagSeparation(parent)
            if key is not None:
                parents_dict["arrange"]=key
                parents_dict["tag"]=parent
            self.separationResult.append(parents_dict)
    def child_tags(self):
        for parent in self.separationResult:
            tag=parent["tag"]
            list_children=[]
            children=self.__trickleDown(tag,list_children)
    def __trickleDown(self,tag,list_children):
        """태그 및으로 내리면서 찾기"""
        child_tags=list(filter(lambda x: isinstance(x, Tag), tag.contents))
        if not child_tags:
            return
        else:
            for child in child_tags:
                separation=self.__tagSeparation(child)
                if separation is not None:
                    list_children.append({"arrange":separation,"tag":child})
                return self.__trickleDown(child,list_children)

class ResultDict(object):
    def __init__(self):
        self.diction={}
    def __setitem__(self, key, value):
        self.diction[key]=value
    def __getitem__(self, key):
        return self.diction.get(key)
    def resultDiction(self):
        return self.diction

class Quotation(ResultDict):
    def __init__(self,quotation_tag):
        self.quotation_tag=quotation_tag
        super().__init__()
        self['type']='quotation'
    def get_id(self):
        class_id = self.quotation_tag.attrs.get('id')
        self['id'] = class_id if class_id is not None else ""

    def get_contents(self):
        self['contents']={}
        self["contents"]["text"] = []
        list_p = self.quotation_tag.find_all("p")
        for p in list_p:
            p_style = p.attrs.get('style')
            span = p.find("span")
            span_style = span.attrs.get('style')
            text = span.text
            self["contents"]["text"].append(
                {"p_style": p_style if p_style is not None else '',
                 "s_style": span_style if span_style is not None else '',
                 "text": text})
class Title(ResultDict):
    def __init__(self,tagTitle):
        self.tagTitle=tagTitle
        super().__init__()
        self["type"]='title'
    def get_id(self):
        class_id = self.tagTitle.attrs.get('id')
        self['id'] = class_id if class_id is not None else ""

    def get_contents(self):
        self["contents"] = {}
        list_texts=self.tagTitle.find_all("span")
        text_group=list(map(lambda x:x.text,list_texts))
        self["contents"]["texts"]=text_group
class Map(ResultDict):
    def __init__(self,mapTag):
        self.mapTag=mapTag
        super().__init__()
        self["type"]='map'
    def get_id(self):
        class_id = self.mapTag.attrs.get('id')
        self['id'] = class_id if class_id is not None else ""
    def get_contents(self):
        self["contents"]={}
        map_img = self.mapTag.find("img")
        # print(map_img)
        self["contents"]["map_img_src"]=map_img.attrs.get('src') if map_img is not None else ''
        a = self.mapTag.find("a")
        """https://map.naver.com/v5/entry/place/33134036?id=33134036"""
        data_link = a.attrs.get('data-linkdata')
        if data_link is not None:
            data_link = json.loads(data_link)
        else:
            data_link={}
        self["contents"]['map_data'] = data_link
        self["contents"]['map_src'] = """https://map.naver.com/v5/entry/place/{map_id}?id={map_id}""".format(
            map_id=data_link.get('placeId') if data_link else '')
class MrBlog(ResultDict):
    def __init__(self,mrblog_tag):
        self.mrblog_tag=mrblog_tag
        super().__init__()
        self['type']="mrBlog"
    def get_id(self):
        class_id = self.mrblog_tag.attrs.get('id')
        self['id'] = class_id if class_id is not None else ""
    def get_contents(self):
        self["contents"]={}
        strongs = self.mrblog_tag.find_all("strong")
        self["contents"]['text'] = {"all_texts": self.mrblog_tag.text}
        list_strong = []
        for strong in strongs:
            list_strong.append({"text": strong.text})
        self["contents"]["strong"] = list_strong
        ps = self.mrblog_tag.find_all("p")
        list_p = []
        for p in ps:
            list_p.append({"text": p.text})
        self['contents']['p'] = list_p
class Table(ResultDict):
    def __init__(self,table_tag):
        self.table_tag=table_tag
        super().__init__()
        self["type"]="table"
    def get_id(self):
        class_id = self.table_tag.attrs.get('id')
        self['id'] = class_id if class_id is not None else ""
    def get_contents(self):
        self["contents"]={}
        table_style = self.table_tag.find("div", {"class": "se-section se-section-table se-l-default se-section-align-"})
        self["contents"]["style"] = table_style.attrs.get('style')
        table_body = self.table_tag.find("tbody")
        table_rows = table_body.find_all("tr")
        row_list = []
        for row in table_rows:
            list_col = []
            for col in row.contents:
                list_col.append({"style": col.attrs.get('style') if col.attrs.get('style') is not None else '', 'contents': col.text})
            row_list.append(list_col)
        self["contents"]['table'] = row_list
class Video(ResultDict):
    def __init__(self,video_tag):
        self.video_tag=video_tag
        super().__init__()
        self['type']='video'
    def get_id(self):
        class_id = self.video_tag.attrs.get('id')
        self['id'] = class_id if class_id is not None else ""
    def get_contents(self):
        self['contents']={}
        iframe = self.video_tag.find("iframe")
        self['contents']['video_tags']={}
        self['contents']['video_tags']['video_tag_info'] = iframe.attrs
        self['contents']['video_tags']['video_tag_source'] = str(iframe)
        self['contents']['video_tags']['video_src'] = iframe.attrs['src']
        script = self.video_tag.find("script")
        video_datamodule = script.attrs.get('data-module')
        if video_datamodule is not None:
            video_datamodule = json.loads(video_datamodule)
        else:
            video_datamodule={}
        self['contents']['script'] = video_datamodule
class Oglink(ResultDict):
    def __init__(self,oglink_tag):
        self.oglink_tag=oglink_tag
        super().__init__()
        self['type']='oglink'
    def get_id(self):
        class_id = self.oglink_tag.attrs.get('id')
        self['id'] = class_id if class_id is not None else ""


    def get_contents(self):
        self['contents']={}
        a_thumbnail = self.oglink_tag.find("a", {"class": "se-oglink-thumbnail"})

        thumb_href = a_thumbnail.attrs.get('href')
        img_thumbnail = a_thumbnail.find("img")
        thumb_img_url = img_thumbnail.attrs.get('src')
        self['contents']['thumbnail'] = {'thumb_href': thumb_href if thumb_href is not None else '',
                                         'thumb_img': thumb_img_url if thumb_img_url is not None else ''}
        link_info = self.oglink_tag.find("a", {"class": "se-oglink-info"})
        link_href = link_info.attrs.get('href')
        title = link_info.find("strong", {"class": "se-oglink-title"}).text
        summary = link_info.find("p", {"class": "se-oglink-summary"}).text
        original_url = link_info.find("p", {"class": "se-oglink-url"}).text
        self['contents']['link_detail'] = {"title": title,
                                           "summary": summary,
                                           "base_url": original_url,
                                           'href': link_href if link_href is not None else ''}
        script = self.oglink_tag.find("script")
        data_module = script.attrs.get('data-module')
        if data_module is not None:
            data_module = json.loads(data_module)
        else:
            data_module={}
        self['contents']['script'] = data_module
class Image(ResultDict):
    def __init__(self,img_tags):
        self.img_tags=img_tags
        super().__init__()
        self['type']='image'
    def get_id(self):
        class_id = self.img_tags.attrs.get('id')
        self['id'] = class_id if class_id is not None else ""


    def remove_blur(self,file_name):
        return str(file_name).replace("_blur", "0")
    def get_contents(self):
        self["contents"] = {}
        self["contents"]['img']=[]
        modules = self.img_tags.find_all("div", {"class": "se-module se-module-image"})
        for module in modules:
            module_style = module.attrs.get('style')
            a = module.find("a")
            img_a_data = a.attrs.get('data-linkdata')
            if img_a_data is not None:
                dict_img_a_data = json.loads(img_a_data)
            else:
                dict_img_a_data = {}
            try:
                image_tag = a.find("img").attrs
            except:
                image_tag={}
            else:
                image_tag['src'] = self.remove_blur(image_tag['src'])
            self['contents']["img"].append({"style": module_style, "href_data": dict_img_a_data, "img_lazyTag": image_tag})
        texts = self.img_tags.find_all("span")
        list_text = []
        for text in texts:
            list_text.append({"style": text.attrs['style'] if text.attrs.get('style') is not None else '', "text": text.text})
        self['contents']["text"] = list_text
class Oembed(ResultDict):
    def __init__(self,oembedTag):
        self.oembedTag=oembedTag
        super().__init__()
        self['type']='oembed'
    def get_id(self):
        class_id = self.oembedTag.attrs.get('id')
        self['id'] = class_id if class_id is not None else ""
    def get_contents(self):
        iframe = self.oembedTag.find("iframe")
        str_iframe = str(iframe)
        script = self.oembedTag.find("script")
        data = script.attrs.get('data-module')
        if data is not None:
            data = json.loads(data)
        else:
            data = {}
        self["contents"]={}
        self["contents"]["embed_tag"]= str_iframe
        self["contents"]["embed_details"] = data
class StickerTag(ResultDict):
    def __init__(self,stickerTag):
        """{"type":"sticker","id":id,"contents":[{"data_linkdata":data,"img":img}]}"""
        self.stickerTag=stickerTag
        super().__init__()
        self['type']='sticker'
    def get_id(self):
        class_id = self.stickerTag.attrs.get('id')
        self['id'] = class_id if class_id is not None else ""
    def get_contents(self):
        list_a = self.stickerTag.find_all("a")
        self["contents"] = []
        for a in list_a:
            data_linkdata = a.attrs.get('data-linkdata')
            if data_linkdata is not None:
                dict_data_linkdata = json.loads(data_linkdata)
            else:
                dict_data_linkdata = {}
            img = a.find("img")
            try:
                img_data = img.attrs
            except:
                img_data = {}
            self["contents"].append({"data_linkdata": dict_data_linkdata, "img": img_data})
class HorizontalTag(ResultDict):
    def __init__(self,horizontalTag):
        self.horizontalTag=horizontalTag
        super().__init__()
        self['type']='horizontal_line'
    def get_id(self):
        class_id = self.horizontalTag.attrs.get('id')
        self['id'] = class_id if class_id is not None else ""

    def get_contents(self):
        self['contents']={}
        self["contents"]['all_contents']='\n'
class TextTag(ResultDict):
    def __init__(self,textTag):
        self.textTag=textTag
        super().__init__()
        self['type']='text'
    def get_id(self):
        class_id=self.textTag.attrs.get('id')
        self['id'] = class_id if class_id is not None else ""
    def get_contents(self):
        self['contents']={}
        whole_text=self.textTag.text
        self['contents']['all_contents']=whole_text
        text_spans = self.textTag.find_all("span")
        self['contents']['contents_separation']=[]
        for span in text_spans:
            style = span.attrs.get("style")
            style = style if style is not None else ""
            id = span.attrs.get("id")
            id = id if id is not None else ""
            span_text = span.text
            self['contents']['contents_separation'].append({"style":style,"id":id,"span_text":span_text})


if __name__ == '__main__':
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"}
    url = "https://m.blog.naver.com/inzzang9807/222005907447"
    r = requests.get(url, headers=headers)
    req = r.text
    r.close()
    soup = BeautifulSoup(req, 'html.parser')
    title = soup.find("title").text.replace(" : 네이버 블로그", '')
    contents_main = soup.find("div", {"class": "se-main-container"})

    instance_tagManager=TagManager(contents_main)
    instance_tagManager.parents_tags()
    instance_tagManager.child_tags()
    print("stop")