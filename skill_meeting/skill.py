import logging
from typing import List, Dict

import markdown

from opsdroid import events
from opsdroid.skill import Skill
from opsdroid.matchers import match_event, match_parse

log = logging.getLogger("skill_meeting.skill")


ITEM_TEMPLATE = """\
* {title}

    {body}
"""

AGENDA_TEMPLATE = """\
# Agenda
{items}
"""

class Meeting(Skill):
    """
    Manage meetings with opsdroid.
    """
    async def extend_agenda(self, title: str, body: str) -> None:
        """
        Extend the existing agenda in memory.
        """
        agenda = await self.opsdroid.memory.get("agenda")
        agenda = agenda or []
        agenda.append({"title": title, "body": body})
        await self.opsdroid.memory.put("agenda", agenda)

    async def generate_agenda_md(self, agenda: List[Dict[str, str]]) -> str:
        items = [ITEM_TEMPLATE.format(**item) for item in agenda]
        return AGENDA_TEMPLATE.format(items="\n".join(items))

    @match_parse('!agenda "{title}" "{body}"')
    @match_parse('!agenda {title}')
    async def add_to_agenda(self, message: events.Message) -> None:
        title = message.parse_result["title"]
        body = ""
        if "body" in message.parse_result:
            body = message.parse_result["body"]
        await self.extend_agenda(title, body)

        await message.respond("Added to the agenda.")

    @match_parse('!agenda')
    async def show_agenda(self, message: events.Message) -> None:
        agenda = await self.opsdroid.memory.get("agenda")
        if agenda:
            await message.respond(markdown.markdown(await self.generate_agenda_md(agenda)))
        else:
            await message.respond("There is no agenda yet.")

    @match_parse('!agenda clear')
    async def clear_agenda(self, message: events.Message) -> None:
        self.opsdroid.memory.put("agenda", None)
