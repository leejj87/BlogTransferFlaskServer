from . import selenium_management
from ..log import dbMangements as logs
from flask import request
from flask import Flask
from sys import version
from rq import Queue
from worker import conn
from rq.job import Job
from flask import jsonify
q=Queue(connection=conn)
app=Flask(__name__)
app.config['JSON_AS_ASCII']=False
@app.route("/")
def index():
    return "uWSGI from python version: <br>" + version
@app.route('/naver', methods=['GET'])
def naver():
    #start = datetime.datetime.now()
    naverID = request.args.get('naverID')
    content_number = request.args.get('article')
    url="https://blog.naver.com/{0}/{1}".format(naverID,content_number)
    job= q.enqueue_call(func=selenium_management.request_code_parsing,args=(url,))
    job_id=job.get_id()
    return_result=get_result(job_id)
    if isinstance(return_result,str):
        #error status
        return jsonify(status="Error",message=return_result)
    else:
        title, source, result_list, list_hashtags = return_result
        return jsonify(title=title, source=source, details=result_list, tag=list_hashtags)
def get_result(job_key):
    while True:
        job = Job.fetch(job_key, connection=conn)
        value=job.return_value
        if value is None:
            import time
            time.sleep(1)
        else:break
    return value
@app.errorhandler(404)
def page_not_found(error):
	app.logger.error(error)
	logs.addToSystemLogs("404",str(error))
	return "<p>WRONG URL!!</p>"


@app.route('/logs')
def log():
    list_logs=logs.getLogs()

    list_logs=list(map(lambda x:"<p>"+'\t'.join(list(map(lambda y:str(y),x)))+"</p>", list_logs))
    return ''.join(list_logs)
@app.route('/systemlogs')
def systemlog():
    list_logs = logs.getSystemLogs()
    list_logs = list(map(lambda x: "<p>" + '\t'.join(list(map(lambda y: str(y), x))) + "</p>", list_logs))
    return ''.join(list_logs)