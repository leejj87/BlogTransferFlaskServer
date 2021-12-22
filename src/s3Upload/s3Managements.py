import boto3
import requests
import io
from .__init__ import AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY,AWS_DEFAULT_REGION,AWS_BUCKET_NAME,CORES
from concurrent.futures import ThreadPoolExecutor, as_completed
class RequestsRawFiles(object):
    def __init__(self,urls,instance_requests,max_workers=CORES):
        self.urls=urls
        self.instance_requests=instance_requests
        self.results={}
        self.max_workers=max_workers
    def raw_file(self,url):

        raw_file=self.instance_requests.get(url,stream=True)
        raw_data=raw_file.content
        raw_file.close()
        return raw_data,url
    def multiprocessing(self):
        process=[]
        result={}
        with ThreadPoolExecutor(max_workers=self.max_workers) as excutor:
            for url in self.urls:
                process.append(excutor.submit(self.raw_file,url))
        for index,task in enumerate(as_completed(process)):
            try:
                results=task.result()
            except:
                result[index]=None
            else:
                result[index]=results
        return result
class Uploads(RequestsRawFiles):
    def __init__(self,tuple_imgs,blog_id,article_number,instance_requests):
        self.tuple_imgs=tuple_imgs
        self.blog_id=blog_id
        self.article_number=article_number
        self.s3=boto3.resource('s3',
                    aws_access_key_id=AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                    region_name=AWS_DEFAULT_REGION)
        self.buckets = self.s3.Bucket(name=AWS_BUCKET_NAME)
        self.instance_requests=instance_requests
        self.return_url="""https://"""+AWS_BUCKET_NAME+""".s3."""+AWS_DEFAULT_REGION+""".amazonaws.com/{}"""
        super().__init__(self.tuple_imgs,self.instance_requests)
    def uploadsToS3(self):
        process = []
        dict_return={}
        rawURL_dict = self.multiprocessing()
        with ThreadPoolExecutor(max_workers=CORES) as excutor:
            for index, values in rawURL_dict.items():
                if values is None:continue
                process.append(excutor.submit(self.upload, index,values))
        for index, task in enumerate(as_completed(process)):
            try:
                original_url,new_url = task.result()
            except Exception as err:
                print(err)
                dict_return[original_url]=original_url
            else:
                dict_return[original_url]=new_url
        return dict_return
    def upload(self,index,values):
        raw,url=values
        key=self.blog_id+'/'+self.article_number+'/'+str(index)+'.jpg'
        self.buckets.put_object(Key=key, Body=io.BytesIO(raw), ContentType='image/jpg')
        return url,self.return_url.format(key)


if __name__ == '__main__':

    """https://mk87-flaskserver-prod.s3.ap-northeast-2.amazonaws.com/ellyplus_222544391503_0.jpg"""

    r=requests
    imgs=["https://postfiles.pstatic.net/MjAyMTEwMjFfMjM5/MDAxNjM0NzkxMDI0MDY3.FXZyBm8rUBV0uTFiMkovHfHayhQPcKV4NyvJjjSzO8kg.qLKGOTtsBofSJkn1wnlQzPYTT-e4H1JkAx7we8uKf_0g.JPEG.ellyplus/1634790988952.jpg?type=w773",
          "https://postfiles.pstatic.net/MjAyMTEwMjFfMjg2/MDAxNjM0NzkxMDA5ODA3.suPJEbLGcun7-Gnbc5At48xVhqT_AhYoeU6J6B0OGkEg.hLnTmMnhbm_Q7dgPWrRQ2QV3HWzfTVvwq6JiI971Mucg.JPEG.ellyplus/1634768823181.jpg?type=w773",
          "https://postfiles.pstatic.net/MjAyMTEwMjFfMTkw/MDAxNjM0NzkyNTc2MTI5.Sd9wn5EzpE_SV9awk_dIirAR0Clzvfo5dOUQ7kECU7wg.bu-qwtFo5W6w433X5Mom2yB05yABiWFJuz8ejbu5dicg.JPEG.ellyplus/SE-75a2b1ce-3228-11ec-890b-d39a1dd8da48.jpg?type=w773"]


    a=Uploads(imgs,"ellyplus2","222544391503",r)
    print(a.uploadsToS3())









