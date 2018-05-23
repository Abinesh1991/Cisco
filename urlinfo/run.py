from flask import Flask
from flask import jsonify
from flask import request
from flask_pymongo import PyMongo
import json
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'urlinfo'
mongo = PyMongo(app)


def config_logging():

    address="/tmp"
    file = address + '/urlInfo.log'
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    syslog_handler = RotatingFileHandler(file, maxBytes=10 * 1024 * 1024, backupCount=5)
    syslog_handler.setLevel(logging.DEBUG)
    syslog_handler.setFormatter(formatter)
    app.logger.propagate = False
    app.logger.setLevel(logging.DEBUG)
    app.logger.addHandler(syslog_handler)
    handlers = app.logger.handlers
    if len(handlers) > 0:
        app.logger.removeHandler(handlers[0])
    app.logger.addHandler(syslog_handler)

config_logging()

@app.errorhandler(404)
def not_found(error=None):
    message = {
            'status': 404,
            'message': 'Given URL data is not found',
    }
    resp = jsonify(message)
    resp.status_code = 404
    app.logger.error("Given URL data is not found")
    return resp

@app.route("/urlinfo/1/<host>/<path>",methods=['GET'])
def getUrlStatus(host,path):
    """
    This route will fetch the data from db and send the response if
    the given url is malformed or not
    :param host: host with port (ex -- hacker.com:5060)
    :param path: the url path(ex - "var-log-")
    :return: the response with status code
    """
    get_data = mongo.db.url
    path = path.replace("-","/")
    app.logger.info("This is the path :"+path)
    out = get_data.find_one({"$and": [{"host": host}, {"url": path}]})
    if out == None:
        app.logger.info("Given details not found in the DB")
        return not_found()
    else:
        output ={"description":out["description"],"status":out["status"]}
        resp = jsonify({'result': output})
        app.logger.info(output)
        resp.status_code = 200
        return resp


@app.route("/add",methods=['POST'])
def addUrl():
    """
    This Route is to add the host,url,status and description
    This is just for add into the DB.
    We cam have logic where if the URL is valid not .

    :return:
    """
    urlinfo = mongo.db.url
    data = request.data
    dataDict = json.loads(data)
    try:
        host = dataDict['host']
        url = dataDict['url']
        status = dataDict['status']
        description = dataDict['description']
    except:
        app.logger.info(data)
        app.logger.error("Paramter formate is not correct")
        output = {'Result': 'Please send formated data',"status_code":400}
    try:
        put_url= urlinfo.insert({'host':host, 'url': url,"status":status,"description":description})
        output = {'Result': 'Success',"status_code":200}
    except Exception as e:
        output = {'Result': 'Failed',"status_code":400}
        app.logger.error("Failure in adding data to the DB",e)

    resp = jsonify({'result': output})
    return resp

if __name__ == "__main__":
    app.run()