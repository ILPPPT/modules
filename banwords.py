from .. import utils, loader
from time import sleep

@loader.tds 
class BanWordsMod(loader.Module):
    """Плохие слова."""
    strings = {'name': 'BanWords'}

    async def client_ready(self, client, db):
        self.db = db

    async def addbwcmd(self, message):
        """Добавить слово в список "Плохих слов". Используй: .addbw <слово>."""
        if not message.is_private:
            chat = await message.get_chat()
            if not chat.admin_rights and not chat.creator:
                return await message.edit("<b>Я не админ здесь.</b>")
            else:
                if chat.admin_rights.delete_messages == False:
                    return await message.edit("<b>У меня нет нужных прав.</b>")
        words = self.db.get("BanWords", "bws", {})
        args = utils.get_args_raw(message)
        if not args: return await message.edit("<b>[BanWords]</b> Нет аргументов.")
        chatid = str(message.chat_id)
        if chatid not in words:
            words.setdefault(chatid, [])
        if "stats" not in words:
            words.setdefault("stats", {}) 
        if chatid not in words["stats"]:
            words["stats"].setdefault(chatid, {}) 
        if args not in words[chatid]:
            if ", " in args:
                args = args.split(', ')
                words[chatid].extend(args)
                self.db.set("BanWords", "bws", words)
                await message.edit(f"<b>[BanWords]</b> В список чата добавлены слова - \"<code>{'; '.join(args)}</code>\".")
            else:
                words[chatid].append(args)
                self.db.set("BanWords", "bws", words)
                await message.edit(f"<b>[BanWords]</b> В список чата добавлено слово - \"<code>{args}</code>\".")
        else: return await message.edit("<b>[BanWords]</b> Такое слово уже есть в списке слов чата.")
    
    
    async def rmbwcmd(self, message):
        """Удалить слово из список "Плохих слов". Используй: .rmbw <слово или all/clearall (по желанию)>."""
        words = self.db.get("BanWords", "bws", {})
        args = utils.get_args_raw(message) 
        if not args: return await message.edit("<b>[BanWords]</b> Нет аргументов.")
        chatid = str(message.chat_id)
        try:
            if args == "all":
                words.pop(chatid) 
                words["stats"].pop(chatid) 
                self.db.set("BanWords", "bws", words) 
                return await message.edit("<b>[BanWords]</b> Из списка чата удалены все слова.")
            if args == "clearall":
                self.db.set("BanWords", "bws", {}) 
                return await message.edit("<b>[BanWords]</b> Все списки из всех чатов были удалены.")
            words[chatid].remove(args)
            if len(words[chatid]) == 0:
                words.pop(chatid)
            self.db.set("BanWords", "bws", words)
            await message.edit(f"<b>[BanWords]</b> Из списка чата удалено слово - \"<code>{args}</code>\".")
        except KeyError: return await message.edit("<b>Этого слова нет в словаре этого чата.</b>") 
        
    
    async def bwscmd(self, message):
        """Посмотреть список "Плохих слов". Используй: .bws."""
        words = self.db.get("BanWords", "bws", {})
        chatid = str(message.chat_id)
        try: ls = words[chatid] 
        except KeyError: return await message.edit("<b>[BanWords]</b> В этом чате нет списка слов.")
        word = ""
        for _ in ls:
            word += f"• <code>{_}</code>\n"
        await message.edit(f"<b>[BanWords]</b> Список слов в этом чате:\n\n{word}") 
        
        
    async def bwstatscmd(self, message):
        """Статистика "Плохих слов". Используй: .bwstats <clear (по желанию)>."""
        words = self.db.get("BanWords", "bws", {}) 
        chatid = str(message.chat_id)
        args = utils.get_args_raw(message) 
        if args == "clear":
            words["stats"].pop(chatid)
            self.db.set("BanWords", "bws", words) 
            return await message.edit("<b>[BanWords]</b> Статистика пользователей чата сброшена.")
        w = ""
        try:
            for _ in words["stats"][chatid]:
                if _ != "kick" and words["stats"][chatid][_] != 0:
                    user = await message.client.get_entity(int(_)) 
                    w += f'• <a href="tg://user?id={int(_)}">{user.first_name}</a>: <code>{words["stats"][chatid][_]}</code>\n'
            return await message.edit(f"<b>[BanWords]</b> Кто использовал спец.слова:\n\n{w}") 
        except KeyError: return await message.edit("<b>[BanWords]</b> В этом чате нет тех, кто использовал спец.слова.")
        
    
    async def swbwcmd(self, message):
        """Переключить режим "Плохих слов". Используй: .swbw"""
        words = self.db.get("BanWords", "bws", [])
        args = utils.get_args_raw(message)
        chatid = str(message.chat_id)
        
        if chatid not in words:
            words.setdefault(chatid, [])
        if "stats" not in words:
            words.setdefault("stats", {}) 
        if chatid not in words["stats"]:
            words["stats"].setdefault(chatid, {})  
        if "kick" not in words["stats"][chatid]:
            words["stats"][chatid].setdefault("kick", None) 
            
        if words["stats"][chatid]["kick"] == False or words["stats"][chatid]["kick"] == None:
            words["stats"][chatid]["kick"] = True
            self.db.set("BanWords", "bws", words) 
            return await message.edit("<b>[BanWords]</b> Режим кик участников включен.\nЛимит: 5 спец.слова.") 
            
        elif words["stats"][chatid]["kick"] == True:
            words["stats"][chatid]["kick"] = False
            self.db.set("BanWords", "bws", words)
            return await message.edit(f"<b>[BanWords]</b> Режим кик участников выключен.")
            
            
    async def watcher(self, message):
        """мда"""
        if message.sender_id == (await message.client.get_me()).id: return
        words = self.db.get("BanWords", "bws", [])
        chatid = str(message.chat_id)
        userid = str(message.sender_id) 
        user = await message.client.get_entity(int(userid)) 
        if chatid not in str(words): return 
        if userid not in words["stats"][chatid]:
            words["stats"][chatid].setdefault(userid, 0)
        ls = words[chatid]
        for _ in ls:
            if _ in message.text.lower().split():
                count = words["stats"][chatid][userid]
                words["stats"][chatid].update({userid: count + 1})
                self.db.set("BanWords", "bws", words)
                if "жаба" in words[chatid]:
                    sleep(35)
                if "kick" in words["stats"][chatid]:
                    if words["stats"][chatid]["kick"] == True:
                       if count == 5:
                           await message.client.kick_participant(int(chatid), int(userid))
                           words["stats"][chatid].pop(userid) 
                           self.db.set("BanWords", "bws", words) 
                           await message.respond(f"<b>[BanWords]</b> {user.first_name} достиг лимит (5) спец.слова, и был кикнут из чата.")
                await message.client.delete_messages(message.chat_id, message.id)