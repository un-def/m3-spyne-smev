# -*- coding: utf-8 -*-

"""
:Created: 3/12/14
:Author: timic
"""
import datetime
import os

from lxml import etree

from .._base import BaseSmev, BaseSmevWsdl
from .._utils import Cap, el_name_with_ns
from spyne_smev import _xmlns as ns

from model import MessageType, ServiceType, HeaderType, AppDocument

try:
    from spyne.protocol.xml.model import complex_from_element as _spyne_cfe
except ImportError:

    # spyne>=2.11.0
    def _complex_from_element(proto, ctx, typeCls, el):
        return proto.complex_from_element(ctx, typeCls, el)

else:

    # spyne<=2.10.10
    def _complex_from_element(proto, ctx, typeCls, el):
        return _spyne_cfe(proto, typeCls, el)


class Smev256Wsdl(BaseSmevWsdl):

    smev_schema_path = os.path.join(
        os.path.dirname(__file__), "../xsd", "smev256.xsd")
    smev_ns = ns.smev256


class Smev256(BaseSmev):
    """
    Имплементация протокола СМЕВ версии 2.5.6
    """

    _smev_schema_path = os.path.join(
        os.path.dirname(__file__), '../xsd', 'smev256.xsd')
    _ns = ns.nsmap256
    _interface_document_type = Smev256Wsdl

    def construct_smev_envelope(self, ctx, message):
        smev_message = self._create_message_element(ctx)
        message_data = self._create_message_data_element(ctx)
        app_data = message_data.find("./{{{smev}}}AppData".format(**self._ns))
        body_response = ctx.out_body_doc.getchildren()[0]
        app_data.extend(body_response.getchildren())
        body_response.clear()
        body_response.append(smev_message)
        body_response.append(message_data)

    def create_in_smev_objects(self, ctx):

        ctx.udc.in_smev_message = _complex_from_element(
            self, ctx, MessageType, ctx.udc.in_smev_message_document)
        if ctx.udc.in_smev_header_document:
            ctx.udc.in_smev_header = _complex_from_element(
                self, ctx, HeaderType, ctx.udc.in_smev_header_document)
        else:
            ctx.udc.in_smev_header = HeaderType()
        if ctx.udc.in_smev_appdoc_document:
            ctx.udc.in_smev_appdoc = _complex_from_element(
                self, ctx, AppDocument, ctx.udc.in_smev_appdoc_document)
        else:
            ctx.udc.in_smev_appdoc = AppDocument()
        ctx.udc.out_smev_message = MessageType(
            Sender=MessageType.Sender(),
            Recipient=MessageType.Recipient(),
            Service=ServiceType())
        ctx.udc.out_smev_header = HeaderType()
        ctx.udc.out_smev_appdoc = AppDocument()

    def _create_message_element(self, ctx):
        """
        Констрирует болванку для smev:Message

        :param ctx: Сквозной контекст метода
        :rtype: lxml.etree.Element
        """
        if getattr(ctx, "udc", None) is None:
            ctx.udc = Cap()
        if not getattr(ctx.udc, "out_smev_message", None):
            ctx.udc.out_smev_object = Cap()

        SMEV = el_name_with_ns(self._ns["smev"])

        root = etree.Element(SMEV("Message"), nsmap={"smev": self._ns["smev"]})
        sender = etree.SubElement(root, SMEV("Sender"))
        etree.SubElement(sender, SMEV("Code")).text = (
            ctx.udc.out_smev_message.Sender.Code
            or self.smev_params.get("SenderCode", ""))
        etree.SubElement(sender, SMEV("Name")).text = (
            ctx.udc.out_smev_message.Sender.Name
            or self.smev_params.get("SenderName", ""))
        recipient = etree.SubElement(root, SMEV("Recipient"))
        etree.SubElement(recipient, SMEV("Code")).text = (
            ctx.udc.out_smev_message.Recipient.Code
            or self.smev_params.get("RecipientCode", "")
            or ctx.udc.in_smev_message.Sender.Code or "")
        etree.SubElement(recipient, SMEV("Name")).text = (
            ctx.udc.out_smev_message.Recipient.Name
            or self.smev_params.get("RecipientName", "")
            or ctx.udc.in_smev_message.Sender.Name or "")
        if ctx.udc.out_smev_message.Originator:
            originator = etree.SubElement(root, SMEV("Originator"))
            etree.SubElement(originator, SMEV(
                "Code")).text = ctx.udc.out_smev_message.Originator.Code or ""
            etree.SubElement(originator, SMEV(
                "Name")).text = ctx.udc.out_smev_message.Originator.Name or ""
        service = etree.SubElement(root, SMEV("Service"))
        etree.SubElement(
            service, SMEV("Mnemonic")).text = self.smev_params.get(
                "Mnemonic", "")
        etree.SubElement(service, SMEV("Version")).text = self.smev_params.get(
            "Version", "")
        etree.SubElement(root, SMEV(
            "TypeCode")).text = ctx.udc.out_smev_message.TypeCode or "GSRV"
        etree.SubElement(root, SMEV(
            "Status")).text = ctx.udc.out_smev_message.Status or "RESULT"
        etree.SubElement(
            root, SMEV("Date")).text = datetime.datetime.utcnow().isoformat()
        etree.SubElement(
            root, SMEV("ExchangeType")).text = self.smev_params.get(
                "ExchangeType", "0")
        if ctx.udc.out_smev_message.RequestIdRef:
            etree.SubElement(
                root, SMEV("RequestIdRef")
            ).text = ctx.udc.out_smev_message.RequestIdRef or ""
        if ctx.udc.out_smev_message.OriginRequestIdRef:
            etree.SubElement(
                root, SMEV("OriginRequestIdRef")
            ).text = ctx.udc.out_smev_message.OriginRequestIdRef or ""
        if "ServiceCode" in self.smev_params:
            etree.SubElement(
                root, SMEV("ServiceCode")
            ).text = self.smev_params.get(
                "ServiceCode", "")
        if ctx.udc.out_smev_message.CaseNumber:
            etree.SubElement(
                root, SMEV("CaseNumber")
            ).text = ctx.udc.out_smev_message.CaseNumber or ""
        if "OKTMO" in self.smev_params:
            etree.SubElement(
                root, SMEV("OKTMO")).text = self.smev_params.get("OKTMO", "")

        return root

    def _create_message_data_element(self, ctx):
        """
        Конструирует болванку для MessageData

        :rtype: lxml.etree.Element
        """
        SMEV = el_name_with_ns(self._ns["smev"])

        root = etree.Element(
            SMEV("MessageData"), nsmap={"smev": self._ns["smev"]})
        etree.SubElement(root, SMEV("AppData"))
        if ctx.udc.out_smev_appdoc.BinaryData:
            app_document = etree.SubElement(root, SMEV("AppDocument"))
            etree.SubElement(
                app_document, SMEV("RequestCode")
            ).text = ctx.udc.out_smev_appdoc.RequestCode
            etree.SubElement(
                app_document, SMEV("BinaryData")
            ).text = ctx.udc.out_smev_appdoc.BinaryData

        return root