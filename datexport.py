#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ctypes import *
import struct
import io
import codecs
import sqlite3

import GlobalVars as gl

datexport = cdll.LoadLibrary('datexport')
datexport.GetSubfileSizes.restype = None
datexport.CloseDatFile.restype = None

def OpenDatFile(handle, file_name, flags):
    # handle: internal index of dat file (more than one file can be opened at once)
    did_master_map = c_int(0)
    block_size = c_int(0)
    vnum_dat_file = c_int(0)
    vnum_game_data = c_int(0)
    dat_file_id = c_ulong(0)
    dat_id_stamp = (c_byte * 64)()
    first_iter_guid = (c_byte * 64)()
    result = datexport.OpenDatFileEx2(c_int(handle), c_char_p(file_name), c_uint(flags), \
                                      byref(did_master_map), byref(block_size), byref(vnum_dat_file),
                                      byref(vnum_game_data), \
                                      byref(dat_file_id), dat_id_stamp, first_iter_guid)
    return result


def GetNumSubfiles(handle):
    return datexport.GetNumSubfiles(c_int(handle))

def GetSubfileSizes(handle, offset, count):
    # offset: index from 0 to (num_subfiles - 1)
    # subfiles appear to be stored in some kind of linked list internally
    file_id = (c_int * count)()
    size = (c_int * count)()

    iteration = (c_int * count)()

    datexport.GetSubfileSizes(c_int(handle), cast(file_id, POINTER(c_int)), \
                              cast(size, POINTER(c_int)), cast(iteration, POINTER(c_int)), \
                              c_int(offset), c_int(count))

    # return 3 lists with file ids, sizes, iterations respectivly
    return list(file_id), list(size), list(iteration)


def GetSubfileSizes_dict(handle, offset, count):
    file_id, size, iteration = GetSubfileSizes(handle, offset, count)
    return {x: (y, z) for x, y, z in zip(file_id, size, iteration)}


def GetSubfileVersion(handle, file_id):
    return datexport.GetSubfileVersion(c_int(handle), c_int(file_id))


def GetSubfileData(handle, file_id, size):
    buf = (c_byte * size)()
    version = c_int()
    datexport.GetSubfileData(c_int(handle), c_int(file_id), cast(buf, POINTER(c_void_p)), \
                             c_int(0), byref(version))
    return bytearray(buf), version.value


def CloseDatFile(handle):
    datexport.CloseDatFile(c_int(handle))


def PurgeSubfileData(handle, file_id):
    # on success returns 0
    return datexport.PurgeSubfileData(c_int(handle), c_int(file_id))


def PutSubfileData(handle, file_id, data, version, iteration):
    buf = (c_ubyte * len(data)).from_buffer_copy(data)

    # returns number of bytes written
    return datexport.PutSubfileData(c_int(handle), c_int(file_id), cast(buf, POINTER(c_void_p)), \
                                    c_int(0), c_int(len(data)), c_int(version), c_int(iteration), c_byte(0))


def Flush(handle):
    datexport.Flush(c_int(handle))


def dword(data):
    return struct.unpack('<I', data)[0]


def byte(data):
    return struct.unpack('<B', data)[0]


def qword(data):
    return struct.unpack('<Q', data)[0]


def is_text_file(file_id):
    return (file_id >> 24) == 0x25


class Fragment:
    def __init__(self, fragment_id=None):
        self.fragment_id = fragment_id
        self.pieces = []
        self.arg_refs = []
        self.arg_strings = []

    def build_from_data(self, data):
        stream = io.BytesIO(data)
        unicode_stream = codecs.getreader('utf-16le')(stream)
        self.fragment_id = qword(stream.read(8))

        num_pieces = dword(stream.read(4))

        for j in range(num_pieces):
            piece_size = byte(stream.read(1))
            if (piece_size & 0x80) != 0:
                piece_size = ((piece_size ^ 0x80) << 8) | byte(stream.read(1))

            some_data = unicode_stream.read(piece_size)
            self.pieces.append(some_data)

        num_unk_3 = dword(stream.read(4))  # some kind of references
        for j in range(num_unk_3):
            self.arg_refs.append(stream.read(4))

        b = byte(stream.read(1))

        for j in range(b):
            self.arg_strings.append([])
            num_unk_4 = dword(stream.read(4))  # num arguments..?
            for k in range(num_unk_4):
                size_unk_5 = byte(stream.read(1))
                if (size_unk_5 & 0x80) != 0:
                    size_unk_5 = ((size_unk_5 ^ 0x80) << 8) | byte(stream.read(1))

                some_data = unicode_stream.read(size_unk_5)
                self.arg_strings[-1].append(some_data)

        stream.close()

    def get_data(self):
        stream = io.BytesIO()
        unicode_stream = codecs.getwriter('utf-16le')(stream)

        stream.write(struct.pack('<Q', self.fragment_id))
        stream.write(struct.pack('<I', len(self.pieces)))

        for piece in self.pieces:
            piece_size = len(piece)
            if piece_size >= 0x80:
                stream.write(struct.pack('<BB', (piece_size >> 8) ^ 0x80, piece_size & 0xFF))
            else:
                stream.write(struct.pack('<B', piece_size))

            unicode_stream.write(piece)

        stream.write(struct.pack('<I', len(self.arg_refs)))

        for v in self.arg_refs:
            stream.write(v)

        stream.write(struct.pack('<B', len(self.arg_strings)))

        for parts in self.arg_strings:
            stream.write(struct.pack('<I', len(parts)))
            for part in parts:
                part_size = len(part)
                if part_size >= 0x80:
                    stream.write(struct.pack('<BB', (part_size >> 8) ^ 0x80, part_size & 0xFF))
                else:
                    stream.write(struct.pack('<B', part_size))

                unicode_stream.write(part)

        data = stream.getvalue()
        stream.close()
        return data


class SubFile:
    def __init__(self, file_id=None, iteration=None):
        self.file_id = file_id
        self.iteration = iteration

    def build_from_data(self, data):
        stream = io.BytesIO(data)
        unicode_stream = codecs.getreader('utf-16le')(stream)

        file_id = dword(stream.read(4))
        if self.file_id is None:
            self.file_id = file_id

        if not self.file_id == file_id:
            print "AAAAAAAAAAAAAAAAAAA"
            print self.file_id
            print "SHOULD BE TURNED TO:"
            print file_id

        assert self.file_id == file_id

        if not is_text_file(self.file_id):
            self.data = data
            stream.close()
            return 0

        # print 'yay', hex(file_id)

        self.unknown_1 = stream.read(4)
        self.unknown_2 = stream.read(1)
        num_fragments = byte(stream.read(1))
        if (num_fragments & 0x80) != 0:
            num_fragments = ((num_fragments ^ 0x80) << 8) | byte(stream.read(1))

        self.fragments = {}  # hashtable
        for i in range(num_fragments):
            # print i, num_fragments, hex(stream.tell())

            current_fragment = Fragment()
            current_fragment.fragment_id = qword(stream.read(8))
            self.fragments[current_fragment.fragment_id] = current_fragment

            num_pieces = dword(stream.read(4))

            for j in range(num_pieces):
                piece_size = byte(stream.read(1))
                if (piece_size & 0x80) != 0:
                    piece_size = ((piece_size ^ 0x80) << 8) | byte(stream.read(1))

                some_data = unicode_stream.read(piece_size)
                current_fragment.pieces.append(some_data)

            num_unk_3 = dword(stream.read(4))  # some kind of references
            for j in range(num_unk_3):
                current_fragment.arg_refs.append(stream.read(4))

            b = byte(stream.read(1))

            '''
            if b != 0:
               #print hex(file_id)
               #print hex(stream.tell())
                exit()
            '''
            for j in range(b):
                current_fragment.arg_strings.append([])
                num_unk_4 = dword(stream.read(4))  # num arguments..?
                for k in range(num_unk_4):
                    size_unk_5 = byte(stream.read(1))
                    if (size_unk_5 & 0x80) != 0:
                        size_unk_5 = ((size_unk_5 ^ 0x80) << 8) | byte(stream.read(1))

                    some_data = unicode_stream.read(size_unk_5)
                    current_fragment.arg_strings[-1].append(some_data)

        assert stream.tell() == len(data)
        stream.close()

        # print 'done'
        return 1

    def get_data(self, args_order = [], args_id = [], mfile_id=None, mfragment_id=None):
        stream = io.BytesIO()
        unicode_stream = codecs.getwriter('utf-16le')(stream)

        stream.write(struct.pack('<I', self.file_id))
        stream.write(self.unknown_1)
        # stream.write('\x00\x00\x00\x00')
        stream.write(self.unknown_2)

        num_fragments = len(self.fragments)
        if num_fragments >= 0x80:
            stream.write(struct.pack('<BB', (num_fragments >> 8) ^ 0x80, num_fragments & 0xFF))
        else:
            stream.write(struct.pack('<B', num_fragments))

        for fragment_id, fragment in self.fragments.iteritems():
            stream.write(struct.pack('<Q', fragment_id))
            stream.write(struct.pack('<I', len(fragment.pieces)))

            for piece in fragment.pieces:
                piece_size = len(piece)
                if piece_size >= 0x80:
                    stream.write(struct.pack('<BB', (piece_size >> 8) ^ 0x80, piece_size & 0xFF))
                else:
                    stream.write(struct.pack('<B', piece_size))

                unicode_stream.write(piece)

            if fragment_id == mfragment_id and len(args_order) > 0:
                print "QQQQQQQQQQQ"
                args_id1 = [int(i) for i in args_id]
                import logging
                logging.info(u"Using fragment")
                print args_id1
                print args_id
                print args_order
                #fragment.arg_refs = [struct.pack('<I', args_id1[args_order[i]]) for i in range(len(args_order))]
                for i in range(len(args_order)):
                    #args_id[i] = struct.pack('<I', args_id1[args_order[i]])
                    fragment.arg_refs[i] = struct.pack('<I', args_id[args_order[i]])
                    # fragment.arg_refs[i] = fragment.arg_refs1[args_order[i]]
                    # fragment.arg_strings[i] = fragment.arg_strings1[args_order[i]]

            stream.write(struct.pack('<I', len(fragment.arg_refs)))
            for v in fragment.arg_refs:
                stream.write(v)

            stream.write(struct.pack('<B', len(fragment.arg_strings)))

            for parts in fragment.arg_strings:
                stream.write(struct.pack('<I', len(parts)))
                for part in parts:
                    part_size = len(part)
                    if part_size >= 0x80:
                        stream.write(struct.pack('<BB', (part_size >> 8) ^ 0x80, part_size & 0xFF))
                    else:
                        stream.write(struct.pack('<B', part_size))

                    unicode_stream.write(part)

        data = stream.getvalue()
        stream.close()
        return data


'''
def merge_data(data_1, data_2):
    stream_1 = io.BytesIO(data_1)
    stream_2 = io.BytesIO(data_2)
    
    file_i
'''
