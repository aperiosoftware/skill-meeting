import logging

import jinja2

from opsdroid.skill import Skill
from opsdroid.matchers import match_event, match_parse

log = logging.getLogger("skill_meeting.skill")


class Meeting(Skill):
    """
    Manage meetings with opsdroid.
    """
    async def extend_agenda(self, title, body):
        """
        Extend the existing agenda in memory.
        """
        agenda = await self.opsdroid.memory.get("agenda")
        agenda = agenda or []
        agenda.append({"title": title, "body": body})
        await self.opsdroid.memory.put("agenda", agenda)

    @match_parse('!agenda "{title}" "{body}"')
    @match_parse('!agenda {title}')
    async def add_to_agenda(self, message):
        title = message.parse_result["title"]
        body = ""
        if "body" in message.parse_result:
            body = message.parse_result["body"]
        await self.extend_agenda(title, body)

    @match_parse('!agenda')
    async def show_agenda(self, message):
        agenda = await self.opsdroid.memory.get("agenda")
        if agenda:
            await message.respond(str(agenda))
        else:
            await message.respond("There is no agenda yet.")

    @match_parse('!agenda clear')
    async def clear_agenda(self, message):
        self.opsdroid.memory.put("agenda", None)
