# -*- coding: utf-8 -*-

#   Quotes module for Friendly-Telegram
#   Copyright (C) 2020 rfoxed (rf0x1d)

#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.

#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.

#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.

#  SOURCE: rf0x3d.su

import os
import logging
import requests

from .. import loader, utils
from PIL import Image
import requests
from datetime import datetime
from asyncio import sleep
import os
from os import remove as RemFile
from urllib.request import urlretrieve
from telethon.tl.types import DocumentAttributeFilename
import json
from requests.exceptions import ConnectionError

logger = logging.getLogger(__name__)


def register(cb):
    cb(DistortMod())


@loader.tds
class DistortMod(loader.Module):
    """Distort a picture for fun"""

    strings = {
        "name": "Distortion",
        "no_reply": "<code>You didn\'t reply to a message.</code>",
        "cant_distort": "<b>I can't distort that!</b>",
        "help": "<b>Reply to an image or sticker to distort it!</b>",
        "processing": "<code>Processing...</code>",
        "api_down": "<b>API Host is unreachable now. Please try again later.</b>",
        "api_error": "<b>API Error occured :)</b>",
        "invalid_token": "<b>Wrong API Token.</b>",
        "quota_expired": "<code>Your account quota has been ended *shrug*</code>",
        "no_image": "<code>Lel no image provided maaan</code>",
        "cannot_resolve_error": "<b>Cannot resovle an error.\nServer returned:</b> <code>{}</code>"
    }

    def __init__(self):
        self.config = loader.ModuleConfig("API_TOKEN", 'bbeb704b-f2b8-4aa5-ae55-a6544755ddeb',
                                          "API Token for distortion.")

    async def client_ready(self, client, db):
        self.client = client
    
    @loader.unrestricted
    @loader.ratelimit
    async def distortcmd(self, message):
        """Usage: .distort (optional: file/force_file/sticker)
        Sends as sticker by default
        Needs an API Token."""
        args = utils.get_args(message)
        reply = await message.get_reply_message()
        if not reply:
            return await utils.answer(message, self.strings('no_reply',
                                                            message))
        
        if reply.media:
            data = await check_media(reply)
            if isinstance(data, bool):
                await utils.answer(message, self.strings('cant_distort', message))
                return
        else:
            return await utils.answer(message, self.strings('help', message))
        await utils.answer(message, self.strings('processing', message))
        path_img = await self.client.download_media(
                    reply,
                    progress_callback=progress,
        )
        image = upload_to_0x0st(path_img)
        token = self.config["API_TOKEN"]
        try:
            requested = requests.post('https://rsdev.ml/dev/distort', data={
                "token": str(token).encode("utf-8"),
                "picture": image.encode('utf-8')
            })
        except ConnectionError:
            return await utils.answer(message, self.strings('api_down',
                                                            message)) 
        if requested.status_code == 500:
            return await utils.answer(message, self.strings('api_error',
                                                            message))
        else:
            requested = requested.json()

        try:
            urlretrieve(requested['success']['file'], 'file.png')
            if len(args) < 1 or args[0].lower() == 'sticker':
                Image.open('file.png').save('file.webp', 'webp')
                async with self.client.action(message.chat_id, 'document') as action:
                    await sleep(2)
                    with open("file.webp", "rb") as file:
                        await utils.answer(message, file)
                RemFile('file.webp')
                RemFile('file.png')
                try:
                    RemFile(path_img)
                except:
                    pass
            else:
                test = args[0].lower()
                if test == 'file':
                    async with self.client.action(message.chat_id, 'document') as action:
                        with open("file.png", "rb") as file:
                            await utils.answer(message, file)
                    RemFile('file.png')
                    try:
                        RemFile(path_img)
                    except:
                        pass
                elif test == 'force_file':
                    async with self.client.action(message.chat_id, 'document') as action:
                        await sleep(2)
                        with open("file.png", "rb") as file:
                            await utils.answer(message, file, force_document=True)
                    RemFile('file.png')
                    try:
                        RemFile(path_img)
                    except:
                        pass
        except KeyError:
            if requested.get('202'):
                if requested['202'] == 'INVALID TOKEN':
                    return await utils.answer(message, self.strings('invalid_token',
                                                                    message))
            elif requested.get('403'):
                if requested['403'] == 'NO_IMAGE_PROVIDED':
                    return await utils.answer(message, self.strings('no_image',
                                                                    message))
            elif requested.get('228'):
                if requested['228'] == "NO_MORE_QUOTA":
                    return await utils.answer(message, self.strings('quota_expired',
                                                                    message))
            else:
                err = self.strings('cannot_resolve_error', message)\
                    .format(str(requested))
                return await utils.answer(message, err)


async def check_media(reply_message):
    if reply_message and reply_message.media:
        if reply_message.photo:
            data = reply_message.photo
        elif reply_message.document:
            if DocumentAttributeFilename(file_name='AnimatedSticker.tgs') in reply_message.media.document.attributes:
                return False
            if reply_message.gif or reply_message.video or reply_message.audio or reply_message.voice:
                return False
            data = reply_message.media.document
        else:
            return False
    else:
        return False

    if not data or data is None:
        return False
    else:
        return data


def upload_to_0x0st(path):
    req = requests.post('https://0x0.st', files={'file': open(path, 'rb')})
    os.remove(path)
    return req.text


def progress(current, total):
	""" Logs the download progress """
	logger.info("Downloaded %s of %s\nCompleted %s", current, total,
			  (current / total) * 100)