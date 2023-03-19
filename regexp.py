import re

re_roster = re.compile(r"(?P<castle>🌑|🐺|🥔|🦅|🦌|🐉|🦈)\W?(?P<guild_name>.+)\n.+\[.\].+")

re_atklist = re.compile(r"(?P<castle>🌑|🐺|🥔|🦅|🦌|🐉|🦈)\W?(?P<guild_name>.+) Attack Rating\n")

re_deflist = re.compile(r"(?P<castle>🌑|🐺|🥔|🦅|🦌|🐉|🦈)\W?(?P<guild_name>.+) Defence Rating\n")

re_headquarter = re.compile(r"You found hidden headquarter (?P<name>.+)\nТо remember the route you associated it with simple combination: (?P<code>.+)")

re_location = re.compile(r"You found hidden location (?P<name>.+'*.+) lvl.(?P<level>\d{2,3})\n(You noticed .+\n)*То remember the route you associated it with simple combination: (?P<code>.+)")

re_map = re.compile(r"\W+State of map:\n.+")

re_guild = re.compile(r"\W+(?P<tag>\[.+\]) (?P<name>.+)\nCommander: .+")

re_ga = re.compile(r"\W+Common Biscuit \nGuilds: (?P<guilds>\d+) \W+(?P<players>\d+)\n.+")

re_me = re.compile(r'(?:.+\n|\n)+'
                   r'(?P<castle>🌑|🐺|🥔|🦅|🦌|🐉|🦈)(?:(?P<g_emoji>\W+))?\[(?P<guild>[\w\d]{2,3})\](?P<name>.+) '
                   r'(?P<class>Knight|Ranger|Sentinel|Alchemist|Blacksmith|Collector|Esquire|Master) of .+\n'
                   r'\W+Level: (?P<level>\d+)\n'
                   r'\W+Atk: (?P<attack>\d+) \W+Def: (?P<defence>\d+)\n'
                   r'\W+Exp: (?P<exp_current>\d+)\/(?P<exp_needed>\d+)\n'
                   r'\W+Hp: (?P<hp>-?\d+)/(?P<hp_max>\d+)\n'
                   r'\W+Stamina: (?P<stamina_current>\d+)/(?P<stamina_max>\d+)(?: \W+(?P<time_remaining>\d+)min)?\n'
                   r'(?:\W+Mana: (?P<mana>-?\d+)/(?P<mana_max>\d+)\n)?'
                   r'\W+(?P<gold>-?\d+) (?:\W+(?P<pouch>\d+) )\W+(?P<gem>\d+)\n\n'
                   r'\W+Equipment (?:\[-\]|\+(?P<eq_attack>\d+)\W+\+(?P<eq_defence>\d+)\W+)\n'
                   r'\W+Bag: (?P<bag_current>\d+)/\d+ /inv\n\n'
                   r'(?:\nPet:\n'
                   r'(?P<pet>.+) \((?P<pet_level>\d+) lvl\) \W+ /pet\n\n)?'
                   r'State:\n'
                   r'(?P<state>.+)\n\n'
                   r'More: /hero'
                   )


iter_re_roster = re.compile(r"#\d{1,2} (?P<pclass>\W?)(?P<sclass>\W*)(?P<level>\d+) \[\W+\] (?P<player>.+)\n?")

iter_re_list = re.compile(r"#\d{1,2} [⚔|🛡](?P<stat>\d+) (?P<player>.+)\n?")

iter_re_orden = re.compile(r"\"(?P<orden>.+)\".*=.*\"(?P<link>/ga_.+)\",*\n?")

iter_re_andy = re.compile(r"\"(?P<texto>.+)\".*=.*\"(?P<link>.+)\",*\n?")

iter_re_stock = re.compile(r"(?P<code>\d+) .+ x (?P<cant>\d+)\n?")

iter_re_map_protected = re.compile(r"(?P<name>.+) lvl.(?P<level>\d{2,3}) was (?P<quality>closely protected|easily protected|protected)\n(?P<wasattack>\W+Attack: )*.+")

iter_re_map_belongs = re.compile(r"(?P<name>.+) lvl.(?P<level>\d{2,3}) belongs to (?P<alliance>\w+ \w+)\.*(?P<quality> Easy win:| Massacre:|:)\n.+") 
