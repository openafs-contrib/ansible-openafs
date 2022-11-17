# Copyright (c) 2020, Sine Nomine Associates
# BSD 2-Clause License

import os
import struct

KEYTAB_MAGIC = 0x0502
KEYTAB_MAGIC_OLD = 0x0501

# See https://www.iana.org/assignments/kerberos-parameters/kerberos-parameters.xhtml       # noqa: E501
ENCTYPES = {
    1: 'des-cbc-crc',
    2: 'des-cbc-md4',
    3: 'des-cbc-md5',
    5: 'des3-cbc-md5',
    7: 'des3-cbc-sha1',
    9: 'dsaWithSHA1-CmsOID',
    10: 'md5WithRSAEncryption-CmsOID',
    11: 'sha1WithRSAEncryption-CmsOID',
    12: 'rc2CBC-EnvOID',
    13: 'rsaEncryption-EnvOID',
    14: 'rsaES-OAEP-ENV-OID',
    15: 'des-ede3-cbc-Env-OID',
    16: 'des3-cbc-sha1-kd',
    17: 'aes128-cts-hmac-sha1-96',
    18: 'aes256-cts-hmac-sha1-96',
    23: 'rc4-hmac',
    24: 'rc4-hmac-exp',
    25: 'camellia128-cts-cmac',
    26: 'camellia256-cts-cmac',
    65: 'subkey-keymaterial',
}
DES_ENCTYPES = (1, 2, 3, 15)


class Keytab:
    """
    Decode keytab files.
    """
    #
    # The following C-like structure definitions illustrate the MIT keytab
    # file format. All values are in network byte order. All text is ASCII.
    #
    #   keytab {
    #       uint16_t file_format_version;                    /* 0x502 */
    #       keytab_entry entries[*];
    #   };
    #   keytab_entry {
    #       int32_t size;
    #       uint16_t num_components;    /* sub 1 if version 0x501 */
    #       counted_octet_string realm;
    #       counted_octet_string components[num_components];
    #       uint32_t name_type;   /* not present if version 0x501 */
    #       uint32_t timestamp;
    #       uint8_t vno8;
    #       keyblock key;
    #       uint32_t vno; /* only present if >= 4 bytes left in entry */
    #   };
    #   counted_octet_string {
    #       uint16_t length;
    #       uint8_t data[length];
    #   };
    #   keyblock {
    #       uint16_t type;
    #       counted_octet_string key;
    #   };

    def __init__(self, filename):
        self.entries = []
        self.name = filename
        self.read(filename)

    def _read_data(self, f, fmt):
        """
        Read one or more data fields.
        """
        size = struct.calcsize(fmt)
        data = f.read(size)
        if len(data) != size:
            raise IOError("Failed to read keytab data.")
        return struct.unpack(fmt, data)  # returns a tuple

    def _read_bytes(self, f):
        """
        Read a byte string.
        """
        length = self._read_data(f, "!H")
        bytes_, = self._read_data(f, "%ds" % length)
        return bytes_

    def _read_string(self, f):
        """
        Read an ascii text string.
        """
        return self._read_bytes(f).decode('ascii')

    def _read_entry(self, f, version):
        """
        Read a keytab entry.
        """
        numc, = self._read_data(f, "!h")
        if version == KEYTAB_MAGIC_OLD:
            numc -= 1
        realm = self._read_string(f)
        components = []
        for _ in range(0, numc):
            components.append(self._read_string(f))
        if version != KEYTAB_MAGIC_OLD:
            self._read_data(f, "!L")  # read past name_type
        timestamp, vno8, eno = self._read_data(f, "!LBH")
        self._read_bytes(f)  # read past key
        principal = "%s@%s" % ('/'.join(components), realm)
        entry = {
            'realm': realm,
            'components': components,
            'principal': principal,
            'timestamp': timestamp,
            'kvno': vno8,
            'eno': eno,
            'enctype': ENCTYPES.get(eno, 'unknown'),
        }
        return entry

    def read(self, path):
        """
        Read a keytab file.
        """
        self.filename = path
        stat = os.stat(path)
        file_size = stat.st_size
        with open(path, 'rb') as f:
            offset = struct.calcsize("!h")
            try:
                version, = self._read_data(f, "!h")
            except IOError:
                version = 0
            if not (version == KEYTAB_MAGIC or version == KEYTAB_MAGIC_OLD):
                raise ValueError("File {0} is not keytab.".format(path))
            while offset < file_size:
                f.seek(offset)
                # record size, not including this field
                size, = self._read_data(f, "!l")
                entry = self._read_entry(f, version)
                self.entries.append(entry)
                # Calculate next record location.
                record_size = struct.calcsize("!l") + size
                offset += record_size
        return

    def find(self, principal):
        """
        Find keytab entries for the given principal.
        """
        entries = []
        for e in self.entries:
            if e['principal'] == principal:
                entries.append(e)
        return entries

    def get_entries(self, principal, kvno=None):
        """
        Return the list of entries for the given principal and kvno.  If knvo
        is not given, then the entries with the largest kvno are returned. None
        is returned if no matches are found.
        """
        if kvno is None:
            kvno = self.get_kvno(principal)
            if kvno is None:
                return None
        entries = []
        for e in self.entries:
            if e['principal'] == principal and e['kvno'] == kvno:
                entries.append(e)
        return entries

    def get_kvno(self, principal):
        """
        Find the largest kvno for the given principal.  None is returned if no
        matches are found.
        """
        kvno = None
        for e in self.entries:
            if e['principal'] == principal:
                if kvno is None or e['kvno'] > kvno:
                    kvno = e['kvno']
        return kvno
