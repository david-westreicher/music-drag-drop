import struct

import pythoncom
from win32com.server.exception import COMException
from win32com.server.policy import DesignatedWrapPolicy
from win32com.server.util import NewEnum
import win32con
import winerror
from winerror import (
    DRAGDROP_S_CANCEL,
    DRAGDROP_S_DROP,
    DRAGDROP_S_USEDEFAULTCURSORS,
    E_NOTIMPL,
    S_OK,
)

def create_drop_files(file_name_array):
    """
    typedef struct _DROPFILES {
        DWORD pFiles;
        POINT pt;
        BOOL fNC;
        BOOL fWide; } DROPFILES, *LPDROPFILES;
    """
    file_name_buffer='\0'.join(file_name_array)+'\0\0'
    file_name_buffer = file_name_buffer.encode()
    fmt="lllll%ss" %len(file_name_buffer)
    dropfiles=struct.pack(fmt, 20, 0, 0, 0, 0, file_name_buffer)
    return dropfiles


class DataObject(DesignatedWrapPolicy):
    _public_methods_ = ["DAdvise", "DUnadvise", "EnumDAdvise", "EnumFormatEtc", "GetCanonicalFormatEtc", "GetData", "GetDataHere", "QueryGetData", "SetData"]
    _com_interfaces_ = [pythoncom.IID_IDataObject]

    def __init__(self, files) -> None:
        self._wrap_(self)
        self.supported_formats = [
            (win32con.CF_HDROP, None, pythoncom.DVASPECT_CONTENT, -1, pythoncom.TYMED_HGLOBAL),
        ]
        self.files = files
    
    def GetData(self, fe):
        cf_in, target_in, aspect_in, index_in, tymed_in  = fe
        if cf_in != win32con.CF_HDROP:
            raise COMException(hresult=E_NOTIMPL)
        print("getdata", fe)
        ret_stg = pythoncom.STGMEDIUM()
        dropfiles = create_drop_files(self.files)
        ret_stg.set(pythoncom.TYMED_HGLOBAL, dropfiles)
        return ret_stg

    def _query_interface_(self, iid):
        if iid==pythoncom.IID_IEnumFORMATETC:
            return NewEnum(self.supported_formats, iid=iid)

    def GetDataHere(self, fe):
        print("getdatahere")
        raise COMException(hresult=winerror.E_NOTIMPL)

    def QueryGetData(self, fe):
        cf_in, target_in, aspect_in, index_in, tymed_in  = fe
        print("querygetdata", fe, self.supported_formats)
        if cf_in != win32con.CF_HDROP:
            raise COMException(hresult=winerror.DV_E_FORMATETC)
        return S_OK

    def GetCanonicalFormatEtc(self, fe):
        print("getcanonical")
        raise COMException(hresult=winerror.E_NOTIMPL)

    def SetData(self, fe, medium):
        print("setdata")
        raise COMException(hresult=winerror.E_NOTIMPL)

    def EnumFormatEtc(self, direction):
        print("enumformat", direction, pythoncom.DATADIR_GET)
        return NewEnum(self.supported_formats, iid=pythoncom.IID_IEnumFORMATETC)

    def DAdvise(self, fe, flags, sink):
        print("dadvise")
        raise COMException(hresult=winerror.E_NOTIMPL)

    def DUnadvise(self, connection):
        print("dunadvise")
        raise COMException(hresult=winerror.E_NOTIMPL)

    def EnumDAdvise(self):
        print("enumdadvise")
        raise COMException(hresult=winerror.E_NOTIMPL)

class DataDrop(DesignatedWrapPolicy):
    _public_methods_ = ["GiveFeedback", "QueryContinueDrag"]
    _com_interfaces_ = [pythoncom.IID_IDropSource]

    def __init__(self) -> None:
        self._wrap_(self)

    def GiveFeedback(self, effect):
        return DRAGDROP_S_USEDEFAULTCURSORS

    def QueryContinueDrag(self, escape_pressed, key_state):
        if escape_pressed:
            return DRAGDROP_S_CANCEL
        if not (key_state & win32con.MK_LBUTTON) and not (key_state & win32con.MK_RBUTTON):
            return DRAGDROP_S_DROP
        return S_OK

def do_drag_drop(files):
    pythoncom.OleInitialize()
    data_object = pythoncom.WrapObject(DataObject(files), pythoncom.IID_IDataObject, pythoncom.IID_IDataObject)
    drop_source = pythoncom.WrapObject(DataDrop(), pythoncom.IID_IDropSource, pythoncom.IID_IDropSource)
    effect_mask = 1
    pythoncom.DoDragDrop(data_object, drop_source, effect_mask)
