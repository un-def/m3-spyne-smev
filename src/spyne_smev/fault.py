# -*- coding: utf-8 -*-

"""               
fault.py
                  
:Created: 19 Aug 2014  
:Author: tim    
"""

from spyne.model.fault import Fault as _Fault


class ApiError(_Fault):
    """
    Специальный exception, который может быть возбужден в api-методе.

    Специальным образом обрабатывается в потомках исходящего протокола
    Soap11WSSE: вместо Fault в body soap-конверта кладется вызываемый
    soap-message c элементом Error внутри.

    В остальных протоколах вёдет себя как обычный Fault

    TODO: пока необходимо явно передавать имя api-метода в котором возбуждается
    исключение
    """

    detail = None
    faultactor = "Server"

    def __init__(
            self, errorCode, errorMessage, messageName):
        self.errorCode = errorCode
        self.errorMessage = errorMessage
        self.messageName = messageName

    @property
    def faultcode(self):
        return self.errorCode

    @property
    def faultstring(self):
        return self.errorMessage

    def __repr__(self):
        return u"Error({0}: {1})".format(self.errorCode, self.errorMessage)

