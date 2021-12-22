import json
from bs4 import BeautifulSoup,Tag
import re
import requests
from . import tag_managerments
from ..s3Upload import s3Managements
from ..log import dbMangements as logs

class Image_Managements(s3Managements.Uploads):
    def __init__(self,r,blog_url,list_code,original_code):
        """r: requests instance
        이미지 업로드, 코드 수정,"""
        self.r=r
        self.blog_url=blog_url
        self.list_code=list_code
        self.original_code=original_code


        if "naver.com" in self.blog_url:
            list_url = self.blog_url.split("/")
            self.get_id = list_url[-2]
            self.post_id = list_url[-1]

    def getImageURLs(self):
        list_image_url=[]
        image_lists=list(filter(lambda x:x['type']=='image',self.list_code))
        for image in image_lists:
            contents_imgs=image['contents']['img']
            for img in contents_imgs:
                url=img['img_lazyTag']['src']
                list_image_url.append(url)

        return list_image_url
    def replacements(self):
        try:
            list_imgs=self.getImageURLs()

            str_code=json.dumps(self.list_code)

            super().__init__(list_imgs,self.get_id,self.post_id,self.r)
            upload_url_map=self.uploadsToS3()

            #print(upload_url_map)
            #find_images=list(map(lambda x:x['contents'],image_lists))
            #소스코드 바꾸기.

            for original_url,changed_url in upload_url_map.items():
                altered_original_url=original_url.split('?')[0]
                self.original_code=self.original_code.replace(original_url,changed_url)
                self.original_code=self.original_code.replace(altered_original_url,changed_url)
                str_code=str_code.replace(original_url,changed_url)
                str_code=str_code.replace(altered_original_url,changed_url)
            self.list_code=json.loads(str_code)
        except Exception as err:
            print(err)

        return self.original_code,self.list_code

class EmbadedCheckGetIFrame(object):
    def __init__(self,contents_main,soup):
        self.contents_main=contents_main
        self.soup=soup

    def check_embadedContents(self):
        list_embaded=self.contents_main.find_all("div",{"class":"se-component se-oembed se-l-default"})
        return list_embaded
    def getIframes(self):
        list_embaded=self.check_embadedContents()
        return_iframes={}
        if list_embaded:
            for embaded in list_embaded:
                id=embaded.attrs['id']
                script=embaded.find("script")
                metadata=script.attrs['data-module']
                json_metadata=json.loads(metadata)
                data=json_metadata.get("data")
                if data is not None:
                    html=data.get("html")
                    attrs=BeautifulSoup(html,"html.parser")
                    iframe=attrs.find("iframe")

                    embaded.contents[1].replace_with(iframe)
                    #print(iframe)
                else:
                    html=None

                return_iframes[id]=html
        return return_iframes
class DecomposeImg(object):
    def __init__(self,bs):
        """bs 인스턴스"""
        self.bs=bs


    def getLinkedImages(self):
        list_id=[]
        for img_instance in self.imgs:
            parents=img_instance.parent
            liked_json=parents.attrs.get('data-linkdata')
            if liked_json is None:continue
            dict_linked=json.loads(liked_json)
            if dict_linked.get('link') != '' and dict_linked.get('link') is not None:
                list_id.append(dict_linked['id'])
        return list_id
    def deCompose(self,bs_instance):
        bs_instance.decompose()
    def ComposeClasses_linked_img(self):
        def getLinkedImages():
            list_id = []
            for img_instance in self.imgs:
                parents = img_instance.parent
                liked_json = parents.attrs.get('data-linkdata')
                if liked_json is None: continue
                dict_linked = json.loads(liked_json)
                if dict_linked.get('link') != '' and dict_linked.get('link') is not None:
                    list_id.append(dict_linked['id'])
            return list_id
        self.imgs = self.bs.find_all("img")
        list_id=getLinkedImages()
        for img in self.imgs:
            parents=img.parent
            liked_json=parents.attrs.get('data-linkdata')
            if liked_json is None:continue
            for id in list_id:
                if id in liked_json:
                    old_parents=parents.parent
                    self.deCompose(old_parents)
    def ComposeClasses_linked_shopping(self):
        shopping_list=self.bs.find_all("div",{"class":"se-component se-material se-l-default"})
        for instance_shopping in shopping_list:
            self.deCompose(instance_shopping)
    def deleteComponents(self):
        self.ComposeClasses_linked_img()
        self.ComposeClasses_linked_shopping()
    @property
    def getBs(self):
        return self.bs
def changeToMobile(url):
    if "naver.com" in url:
        list_url=url.split("/")
        get_id=list_url[-2]
        post_id=list_url[-1]
        list_post_id=re.findall(r'\d+',post_id)
        if list_post_id:
            post_id=list_post_id[0]
            """https://m.blog.naver.com/kingsuda/222533770829"""
            return "https://m.blog.naver.com/{0}/{1}".format(get_id,post_id)
        return None
    else:return None
def remove_blur(file_name):
    return str(file_name).replace("_blur", "0")
class VideoInformation(object):
    """<iframe width="544" height="306" src="https://serviceapi.nmv.naver.com/flash/convertIframeTag.nhn?vid=3C7F7D810A5714C5585B3275E4E523695B09&outKey=V128f09389803abd9d7d41c281b85191072ddb971b247a4c806f91c281b85191072dd" frameborder="no" scrolling="no" title="NaverVideo" allow="autoplay; gyroscope; accelerometer; encrypted-media" allowfullscreen></iframe>


https://serviceapi.nmv.naver.com/flash/getShareInfo.nhn?vid=3C7F7D810A5714C5585B3275E4E523695B09&srcUrl=https%3A%2F%2Fblog.naver.com%2Fdeity030%2F222523686452&title=%ED%95%9C%EB%9D%BC%EB%B4%89%EC%86%8C%EB%85%80&plaerType=html&inKey=V1258cb970e49ce3297451c281b85191072dd7f7353e9320b9454f0938983abd9d7d41c281b85191072dd
https://serviceapi.nmv.naver.com/ui/refererList.nhn?vid=3C7F7D810A5714C5585B3275E4E523695B09&inKey=V1258cb970e49ce3297451c281b85191072dd7f7353e9320b9454f0938983abd9d7d41c281b85191072dd
https://serviceapi.nmv.naver.com/ui/refererList.nhn?vid=0494CB7CC03AEC263DFF198B8C5F07A0D6FB&inKey=V1288ac7f81c0f6338a8dfc491857a7655011b5a7ef4f00dd0823d14b5be69b6891c7fc491857a7655011
V1288ac7f81c0f6338a8dfc491857a7655011b5a7ef4f00dd0823d14b5be69b6891c7fc491857a7655011
https://serviceapi.nmv.naver.com/flash/getShareInfo.nhn?vid=0494CB7CC03AEC263DFF198B8C5F07A0D6FB&srcUrl=https://blog.naver.com/aksrb212/222524330177&title=%ED%95%9C%EB%9D%BC%EB%B4%89%EC%86%8C%EB%85%80&plaerType=html&inKey=V1288ac7f81c0f6338a8dfc491857a7655011b5a7ef4f00dd0823d14b5be69b6891c7fc491857a7655011

{"type":"v2_video", "id" :"SE-a4744366-25c4-4303-a862-00fe0b1da4c0", "data" : { "videoType" : "player", "vid" : "0494CB7CC03AEC263DFF198B8C5F07A0D6FB", "inkey" : "V1288ac7f81c0f6338a8dfc491857a7655011b5a7ef4f00dd0823d14b5be69b6891c7fc491857a7655011", "thumbnail": "https://phinf.pstatic.net/image.nmv/blog_2021_10_02_999/29e1a515-2342-11ec-a8ac-505dac8c35ff_01.jpg", "originalWidth": "1920", "originalHeight": "1080", "width": "886", "height": "498", "contentMode": "extend", "format": "normal", "mediaMeta": {"@ctype":"mediaMeta","title":"단석산 등산","tags":["경주등산","단석산등산","단석산","신선사","마애불상","신선사마애불상군"],"description":"경주시 건천읍 송선리에 있는 단석산 당고개 분기점에서 출발하여, 단석산 정상에 올라 정상 주변을 감상하고, 내려가는길에 신선사에 들러 신선사 마애불상군을 구경하고, 오덕선원을 지나 단석산 가는길이라는 식당을 지나 당고개길로 올라가는 다리를 찾아 원점회기하는 코스이다."}, "useServiceData": "false"}}"""
    def __init__(self,contents_main,soup,blog_url,width='90%',height='50%'):
        """width=90%
        height=50%"""
        self.width=width
        self.soup=soup
        self.height=height
        self.contents_main=contents_main
        self.url=blog_url
        self.base_url="""https://serviceapi.nmv.naver.com/flash/convertIframeTag.nhn?vid={vid}&outKey={inkey}&width={width}&height={height}&title=%ED%95%9C%EB%9D%BC%EB%B4%89%EC%86%8C%EB%85%80&plaerType=html&inKey={inkey}"""
        self.tag="""<iframe width="{width}" height="{height}" src="https://serviceapi.nmv.naver.com/flash/convertIframeTag.nhn?vid={vid}&outKey={inkey}" frameborder="no" scrolling="no" title="NaverVideo" allow="autoplay; gyroscope; accelerometer; encrypted-media" allowfullscreen></iframe>"""
        self.base_url_first="""https://serviceapi.nmv.naver.com/flash/getShareInfo.nhn?vid={vid}&srcUrl={blog_url}&title=%ED%95%9C%EB%9D%BC%EB%B4%89%EC%86%8C%EB%85%80&plaerType=html&inKey={inkey}"""
    def find_videos(self):
        list_videos=self.contents_main.find_all("div",{"class":"se-component se-video se-l-default"})
        #print(list_videos)
        for video in list_videos:
            script=video.find("script")
            str_json=script.attrs.get('data-module')
            if str_json is not None:
                dict_id=json.loads(str_json)

                vid=dict_id['data']['vid']
                inkey=dict_id['data']['inkey']
                outkey=self.__shareAPIToGetOutKey(vid,inkey,self.url)

                #tags=self.tag.format(vid=vid,inkey=inkey,width=self.width,height=self.height)
                new_tag = self.soup.new_tag("iframe", width=self.width,height=self.height,src="https://serviceapi.nmv.naver.com/flash/convertIframeTag.nhn?vid={vid}&outKey={outkey}".format(vid=vid,outkey=outkey),frameborder="no",scrolling="no",title="NaverVideo",allow="autoplay; gyroscope; accelerometer;encrypted-media")
                video.contents[1].replace_with(new_tag)
                #print("check")
        #return self.soup.page_source

    def __shareAPIToGetOutKey(self,vid,inkey,url):
        url=self.base_url_first.format(vid=vid,blog_url=url,inkey=inkey)
        r=requests.get(url)
        txt=r.text
        r.close()

        outkey=re.search(r'outKey=(.*?)&',txt).group(1)
        return outkey
def tagCapture(soup):
    hashTags=soup.find("div",{"class":"post_tag"})
    if hashTags is not None:
        eachHashtags=hashTags.find_all('li')
        return list(map(lambda x:x.text.replace('#',''), eachHashtags))
    else:
        return []


class ContentsArray(object):
    def __init__(self,contents_tags):
        self.contents_tags = contents_tags
        self.class_names=["se-component se-text se-l-default"]
        self.result_list=[]
    def filter_Contents(self):
        taged_lists = list(filter(lambda x: isinstance(x, Tag), self.contents_tags.contents))
        for tag in taged_lists:
            result=tag_managerments.TagManager(tag).tagReturn()
            self.result_list.append(result)
        return self.result_list

    @property
    def getResultLists(self):
        return self.result_list

def request_code_parsing(blog_url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"}
        url = changeToMobile(blog_url)
        #rt = RequestsTor()
        #r = rt.get(url,headers=headers)
        tor_proxy={'http':"socks5h://localhost:9050",
                   'https':"socks5h://localhost:9050"}
        r=requests
        r_get=r.get(url,headers=headers,proxies=tor_proxy)
        req=r_get.text
        r_get.close()
        soup = BeautifulSoup(req, 'html.parser')
        title = soup.find("title").text.replace(" : 네이버 블로그", '')
        list_hashTags=tagCapture(soup)
        contents_main = soup.find("div", {"class": "se-main-container"})
        instance_decompose = DecomposeImg(contents_main)
        instance_decompose.deleteComponents()
        changed_source = instance_decompose.getBs
        # video change
        instance_video = VideoInformation(changed_source, soup, url,width='90%',height='50%')
        instance_video.find_videos()
        #embaded add Iframe
        instance_embaded = EmbadedCheckGetIFrame(changed_source, soup)
        instance_embaded.getIframes()
        # last change blur
        original_source=changed_source
        result_list=ContentsArray(original_source).filter_Contents()
        source_without_delete = str(changed_source).replace("_blur", "0")
        #print(title,source_without_delete,result_list)
        Image_management_instance=Image_Managements(r,blog_url,result_list,source_without_delete)
        source_without_delete, result_list=Image_management_instance.replacements()
        #return title, source_without_delete, result_list
    except Exception as err:
        print(err)
        logs.addToMainLogs(blog_url,'ERROR',"selenium_management.py",str(err).replace('"','').replace("'",''))
        #utility.logs_main(blog_url+'\t'+'ERRORS'+'\t'+str(err))
        return str(err)
    else:
        logs.addToMainLogs(blog_url,"SUCCESS",'','')
        #utility.logs_main(blog_url+'\t'+'SUCCESS')
        return title, source_without_delete, result_list, list_hashTags
if __name__ == '__main__':
    request_code_parsing("https://blog.naver.com/yjhedc/222542327407")