from torch.utils.data import IterDataPipe
from typing import Iterable, Iterator, Tuple
from io import BufferedIOBase

import os
import tarfile
import warnings

class TarArchiveReaderIterDataPipe(IterDataPipe[Tuple[str, BufferedIOBase]]):
    r""" :class:`TarArchiveReaderIterDataPipe`.

    Iterable datapipe to extract tar binary streams from input iterable which contains pathnames,
    yields a tuple of pathname and extracted binary stream.

    Args:
        datapipe: Iterable datapipe that provides pathnames
        mode: File mode used by `tarfile.open` to read file object.
            Mode has to be a string of the form 'filemode[:compression]'
        length: a nominal length of the datapipe

    Note:
        The opened file handles will be closed automatically if the default DecoderDataPipe
        is attached. Otherwise, user should be responsible to close file handles explicitly
        or let Python's GC close them periodly.
    """
    def __init__(
        self,
        datapipe: Iterable[str],
        mode: str = "r:*",
        length: int = -1
    ):
        super().__init__()
        self.datapipe: Iterable[str] = datapipe
        self.mode: str = mode
        self.length: int = length

    def __iter__(self) -> Iterator[Tuple[str, BufferedIOBase]]:
        for pathname in self.datapipe:
            if not isinstance(pathname, str):
                raise TypeError(f"pathname should be of string type, but is type {type(pathname)}")
            try:
                tar = tarfile.open(name=pathname, mode=self.mode)
                for tarinfo in tar:
                    if not tarinfo.isfile():
                        continue
                    extracted_fobj = tar.extractfile(tarinfo)
                    if extracted_fobj is None:
                        warnings.warn("failed to extract file {} from source tarfile {}".format(tarinfo.name, pathname))
                        raise tarfile.ExtractError
                    inner_pathname = os.path.normpath(os.path.join(pathname, tarinfo.name))
                    yield (inner_pathname, extracted_fobj)  # type: ignore[misc]
            except Exception as e:
                warnings.warn(
                    "Unable to extract files from corrupted tarfile stream {} due to: {}, abort!".format(pathname, e))
                raise e

    def __len__(self):
        if self.length == -1:
            raise TypeError("{} instance doesn't have valid length".format(type(self).__name__))
        return self.length
