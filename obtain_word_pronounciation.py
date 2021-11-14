"""The objective of this script is to obtain the mp3 sound file associated
with each of the words of the [word file] on the "https://ordnet.dk/ddo"
website.
"""

import re
import os
import asyncio
import aiohttp
import aiofiles

from typing import Set

###############################################################################
# synchronous read of the words from a file

def get_words(filename: str) -> Set[str]:
    """Obtain the words present in the file [filename].

    Args:
        filename: name of the file that contains the words

    Returns:
        words: words that we want the mp3 sound file of

    Requires:
        filename should be a valid name of a file
        the words in the file [filename] should be in separated lines
    
    Ensures:
        the set of words will only contain unique words and no empty words
    """

    with open(filename, 'r', encoding='utf8') as datafile:
        words = {wrd for wrd in datafile.read().splitlines() if len(wrd) != 0}
    return words


def check_words(all_words: Set[str]) -> Set[str]:
    """Checks if the word already has an associated mp3 sound file. If it does,
    then it removes it from the words whose associated mp3 sound file is going
    to be downloaded.

    Args:
        all_words: unfiltered words which we want the associated mp3 file

    Returns:
          words for which we want the associated mp3 file, but we don't already 
        have the file.
    """

    if os.path.exists("mp3_files"):
        pre_existing_words = set(os.listdir("./mp3_files/"))
        return {word for word in all_words 
                if word + ".mp3" not in pre_existing_words}
    else:
        os.mkdir("mp3_files")
        return all_words


###############################################################################
# asynchronous request of the mp3 files

async def dwn_mp3_file(session: aiohttp.ClientSession, link: str, word: str):
    """Downloads the mp3 sound file from the URL provided to an mp3 file with
    the name of the word from which the link was obtained.

    Args:
        session: http session in which to make the request
        link: URL of the mp3 sound file
        word: word that is pronounciated in the mp3 sound file
    """

    async with session.get(link) as rsp:
        if rsp.status == 200:
            async with aiofiles.open(f"./mp3_files/{word}.mp3", 'wb') as f:
                await f.write(await rsp.read())



async def request_word_page(session: aiohttp.ClientSession, word: str, 
                            pattern: str):
    """Obtains the URL of the mp3 sound file associated with the word [word]
    and downloads the mp3 file.

    Args:
        session: http session in which to make the request
        word: word that we want the associated mp3 file
        pattern: pattern that finds the mp3 file URL
    """

    async with session.get('https://ordnet.dk/ddo/ordbog?query='+ word) as rsp:
        if rsp.status == 200:
            await dwn_mp3_file(session, 
                               re.findall(pattern, await rsp.text())[0], word)


async def make_all_requests(all_words: Set[str]):
    pattern = re.compile('href="([^"]+\.mp3)"')
    async with aiohttp.ClientSession() as session:
        await asyncio.gather(*[request_word_page(session, word, pattern)
                                for word in all_words])


###############################################################################
# joining the two parts

def main(filename: str):
    """Downloads the mp3 sound file associated with each word if it has not
    already been downloaded.

    Args:
        filename: name of the file that contains the words
    
    Requires:
        filename should be a valid name of a file
        the words in the file [filename] should be in separated lines
    """
    all_words = check_words(get_words(filename))
    asyncio.run(make_all_requests(all_words))


###############################################################################

if __name__ == '__main__':
    main('words.txt')