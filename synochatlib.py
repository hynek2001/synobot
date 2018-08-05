"""

"""
from logging import handlers
import logging
import os
from flask import Flask, redirect, url_for, request, Response
import pprint
from multiprocessing import Process
import requests
import json
import random
import string
import threading
import re



class SynoBot(object):
    """
    chat bot for synology chat server
    see: https://www.synology.com/en-us/dsm/feature/chat

    it offer
        * map functions to user's messages
        * function to send question to user, and execute function after answer
        * function to send message
    """


    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    logger = None
    loggingLevel = logging.DEBUG

    synobotURL = ""
    localBotToken = ""
    synologyBotToken = ""
    conversationStructure = {
            "cas": {
                "cmdregex":"cas.*",
                "function":None

            }
        }
    """
    
    """

    activeQuestionStructure = {}
    """
    example
    "<callbackid>":{
      "username": "<username>",
            "userid": [2],
            "function": function,
            "timeout": 300
    }
    """

    # flask
    flaskApp = None

    connected = False
    TIMEOUT = 10  # time in sec after connection to synology is considered as down...

    def genRandomCallbackID(self):
        """
        will return 30 char long string
        :return:
        """
        return ''.join(random.choice(string.ascii_lowercase) for i in range(30))

    def __init__(self,synologyBotToken, localBotToken,synoboturl, conversation):
        """
        :param synologyBotToken:        this is token sent by server @TODO addverification, message is resecived from server
        :param synoboturl:              this is url to be created
        :param conversationStructure:   this is to define structure, for generic conversation
        """
        self.synologyBotToken=synologyBotToken
        self.synobotURL = synoboturl
        self.conversationStructure = conversation
        self.localBotToken=localBotToken
        logfile = self.ROOT_DIR + os.sep + "logs" + os.sep + "synobotlogging.log"
        handler = handlers.TimedRotatingFileHandler(logfile, when="midnight", interval=1)
        handler.setFormatter(logging.Formatter('%(asctime)s  %(levelname)s threadID:%(thread)d %(message)s',
                                               datefmt="%d-%m-%Y %H:%M:%S"))
        self.logger = logging.getLogger()
        self.logger.setLevel(self.loggingLevel)
        self.logger.addHandler(handler)
        self.logger.addHandler(logging.StreamHandler())

        self.logger.debug("__init__: init function finalised ")

        self.initServer()

    def processUserInput(self,msg):
        """
        will process user input at moment of message arrival, will use conversation structure
        in order to get intial user command...
        idea is, this is only initial entry point for conversation with user, which shall be really
        async...
        at moment initial response is receised,   synobot may be sending additional query etc...


        :return: None... it is support to be starting respective functions
        """
        function=None
        for ii in self.conversationStructure:
            res = re.search(self.conversationStructure[ii]['cmdregex'],msg['message'])
            if res !=None:
                function = self.conversationStructure[ii]['function']
                break
        if function != None:
            function(self,msg)
        else:
            help=""
            for ii in self.conversationStructure:
                help+=f"{ii} \n"

            self.sendMSG([int(msg['userId'])],"sorry, i have no idea what you want. See below supported commands:")
            self.sendMSG([int(msg['userId'])], help)


    def isConnected(self):
        """
            this will send message to synology to itself. if message is received, then self.isConnected = True,
            othervice after self.TIMEOUT sec, it set False
            :return: functin will return notthing, be
            #@TODO   finish concept of connection verification...
        """
        self.logger.debug("isConnected: function starting...")
        # @TODO ...
        pass

    #
    # def sendQuestion(self, id, question, answerStructure):
    #     """
    #     this will send question to ID   to
    #     and will wait for answer...
    #     for bot there is always only 1 actual question from certain IT...
    #     :param question:
    #     :param answerStructure:
    #     :return:
    #     """
    #     # @TODO ...
    #     self.logger.debug("sendQuestion: params:  id: {id}, question {que}".format(
    #         id=id,
    #         que=question
    #     ))
    #     pass

    def sendMSG(self, userIDList, msg):
        """
        send message to somebody on server...
        :param userIDList: list of userid to send message
        :param msg:
        :return:
        """
        # @TODO
        assert type(userIDList) == list

        self.logger.debug(f"sendMSG: params: {userIDList} {msg}")
        message = {
            "user_ids": userIDList,
            "text": msg

        }
        payload = {"payload": json.dumps(message)}

        p = Process(target=sendAsyncMSG, args=(self.synobotURL, payload))
        p.start()

    def sendQuestionMSG(self, msg):
        """
        send message to somebody on server...
        :param userIDList: list of userid to send message
        :param msg:
        :return:
        """
        # @TODO
        callback = self.genRandomCallbackID()
        meee = {
            "user_ids": msg['userids'],
            "text": msg['text'],
            "attachments":
                [{"callback_id": callback,
                  "text": "attachment",
                  "actions":

                      msg['actions']

                  }
                 ]

        }

        self.activeQuestionStructure[callback] = {

            "username": "<username>",
            "userid": msg['userids'],
            "function": msg['function'],
            "timeout": 300

        }

        def deleteQuestion(clb):
            self.activeQuestionStructure.pop(clb)

        threading.Timer(msg['timeout'], deleteQuestion, [callback]).start()

        self.logger.debug(f"sendQuestionMSG: params:  {meee}")

        tree = {"text": "Hello World", "user_ids": [2], "attachments":
            [{"callback_id": "abc", "text": "attachment", "actions":
                [{"type": "button", "name": "resp", "value": "ok", "text": "OK", "style": "green"}]}]}

        payload = {"payload": json.dumps(meee)}
        p = Process(target=sendAsyncMSG, args=(self.synobotURL, payload))
        p.start()

    def sendTestQuestion(self):
        def testListener(result):
            logging.error(f"vysledek dotazu je {result}")
            print(f"vysledek dotazu je {result}")

        quest = {
            "userids": [2],
            "text": "sfdfsdfdsfs",
            "timeout": 300,
            "actions": [
                {"type": "button", "name": "resp1", "value": "ok", "text": "OK", "style": "green"}
                ,
                {"type": "button", "name": "resp2", "value": "nok", "text": "NOK", "style": "red"}

            ],
            "function": testListener

        }

        self.sendQuestionMSG(quest)

    def initServer(self):
        """
        flask server initialisation
        :return:
        """
        self.logger.debug("initServer:starting flask app")
        self.flaskApp = FlaskAppWrapper('wrap')
        self.flaskApp.add_endpoint(endpoint='/1231232131321131444332', endpoint_name='getMessage',
                                   handler=self.getMessage)
        self.flaskApp.run(port=7512, host='0.0.0.0', debug=True, threaded=True)  # ,threaded=True)
        self.logger.debug("initServer: flask as threaded started...")

    # @flaskApp.route('/' + "1231232131321131444332", methods=['POST'])
    def getMessage(self):
        """
        process incoming message
        :return:
        """

        self.logger.debug(f"getMessage: robot message received......")
        msg = {
            "message": request.form.get('text', default=''),
            "userId": request.form.get('user_id', default=''),
            "username": request.form.get('username', default=''),
            "postId": request.form.get('post_id', default=''),
            "threadId": request.form.get('thread_id', default=''),
            "timestamp": request.form.get('timestamp', default=''),
            "actions": request.form.get('actions', default=''),
            "callback_id": request.form.get('callback_id', default=''),
            "token": request.form.get('token', default=''),
            "user": request.form.get('user', default=''),
            "payload": request.form.get('payload', default='')

        }
        if msg['payload'] != "":
            self.logger.debug(f"getMessage: oh. and it has payload. let me see if i have such callback in db......")
            tmpM = json.loads(msg['payload'])
            username = tmpM['user'].get("username", "")
            userID = tmpM['user'].get("userId", "")
            callbackID = tmpM['callback_id']
            actionResult = tmpM['actions'][0]['text']

            self.logger.debug("debug getMessage: response on question is here {us} {uid} {cid} {ar}".format(
                us=username,
                uid=userID,
                cid=callbackID,
                ar=actionResult
            ))
            if callbackID in self.activeQuestionStructure:
                self.logger.debug(f"getMessage: yes. i found active callback")
                fnc = self.activeQuestionStructure[callbackID]['function']
                fnc(actionResult)
            return  # no ned to continue...
        else:
            self.logger.debug("getMessage:message received, and in same time there is no active question...... {mm}".format(mm=str(msg)))
            self.logger.debug(
                "getMessage: handing {mm} to conversation processor".format(
                    mm=str(msg)))
            self.processUserInput(msg)

        # conversation..:

        self.logger.debug("getMessage: robot message received...... {mm}".format(mm=str(msg)))
        self.logger.debug("message {msg} received".format(msg=msg))

        # self.sendTestQuestion()

        return ''


class EndpointAction(object):

    def __init__(self, action):
        self.action = action
        self.response = Response(status=200, headers={})

    def __call__(self, *args):
        self.action()
        return self.response


class FlaskAppWrapper(object):
    app = None

    def __init__(self, name):
        self.app = Flask(name)

    def run(self, port=7512, host='0.0.0.0', debug=True, threaded=False):
        self.app.run(port=port, host=host, debug=debug, threaded=threaded)

    def add_endpoint(self, endpoint=None, endpoint_name=None, handler=None):
        self.app.add_url_rule(endpoint, endpoint_name, EndpointAction(handler), methods=['POST', ])


def sendAsyncMSG(url, payload):
    """
    async function for sending messages. It is here, because i cant run function  ( pickle is, if it is inside class)
    :param url:   synchat chat url...
    :param message:
    :param logger: logger
    :return:
    """
    html = requests.post(verify=False, url=url, data=payload)

    print(
        "sendAsyncMSG: message {msg} sent. Return code is {code} Return value from server is {ret}".format(
            msg=payload,
            ret=html.text,
            code=html.status_code
        ))




if __name__ == '__main__':

    def aa(ref,msg):
        ref.sendMSG([2],"oki funguje to !")


    so = SynoBot(
        localBotToken="1231232131321131444332",
        synologyBotToken="OCv6m2Lg0YX9aH9GML5zborEU244eYhHqxl1eXc1OYsVebTXBzcvCx43yo0awh75",
        synoboturl="https://chat.mraky.org/webapi/entry.cgi?api=SYNO.Chat.External&method=chatbot&version=2&token=%22OCv6m2Lg0YX9aH9GML5zborEU244eYhHqxl1eXc1OYsVebTXBzcvCx43yo0awh75%22",
        conversation={
            "cas": {
                "cmdregex":"cas.*",
                "function":aa

            }
        })
