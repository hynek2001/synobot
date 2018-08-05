.. synobot documentation master file, created by
   sphinx-quickstart on Sat Aug  4 15:23:00 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


synology bot integration
=====================================

here is step by step, howto integrate bot. You need access to synology
chat app. This means you need synology NAS etc...


   * create for yourself localBotToken. It shall be string [a-zA-Z0-9] 20 characters long...ie 1234567890abcdefghij. It will be used during integration
   * check what is ip address of bot. Synology chat server shall be able to reach it!
   * log to synology chat(web, or windows client)
   * left click on icon of your user ( top right ), and select integration, then on bots
   * click on create
      * name select as you like
      * to outgoing URL   http://<botip>:7512/<localBotToken>
      * save somewhere incoming URL(synoboturl) and token(synologyBotToken).
      * click on ok, and close windows

usage
===================================


explanation
************

        * localBotToken
            is random string(a-zA-Z0-9). You need this string for
            synology chat server bot integration.....
        * synologyBotToken ( get from synology bot chat integration process )
            is token, which is send by synology chat server.
            Token is part of bot integration window in synology
            chat server
        * synoboturl   ( get from synology bot chat integration process )
            is url of bot integration in synology
        * conversation
            is dict specifying what shall happend if user send
            something to bot



init
****

minimal::

   so = SynoBot(
      localBotToken="1231232131321131444332",
      synologyBotToken="OCv6m2Lg0YX9aH9GML5zborEU244eYhHqxl1eXc1OYsVebTXBzcvCx43yo0awh75",
      synoboturl="https://chat.mraky.org/webapi/entry.cgi?api=SYNO.Chat.External&method"+
      "=chatbot&version=2&token=%22OCv6m2Lg0YX9aH9GML5zborEU244eYhHqxl1eXc1OYsVebTXBzcv"+
      "Cx43yo0awh75%22",
      conversation={}
   })


synobot api
===================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:



.. automodule:: synochatlib
   :members:



