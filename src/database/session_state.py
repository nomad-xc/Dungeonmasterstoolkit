import random
from dataclasses import dataclass, field


@dataclass
class SessionMonster:

    pool_id: int

    name: str

    hp: int
    max_hp: int

    ac: int
    speed: int
    xp: int

    kind: str = "monster"
    random_encounter: bool = False

    behavior: str = ""
    abilities: str = ""


@dataclass
class SceneMap:

    scene_map_id: int

    name: str
    path: str


@dataclass
class MonsterInstance:

    instance_id: int
    template_name: str
    label: str

    hp: int
    max_hp: int

    ac: int
    speed: int
    xp: int

    kind: str = "monster"

    behavior: str = ""
    abilities: str = ""

    conditions: list = field(default_factory=list)

    @property
    def is_defeated(self):
        return self.hp <= 0


class SessionState:

    _pool = []
    _encounter = []

    _initiative = []
    _turn_index = 0
    _round_number = 1

    _next_pool_id = 1
    _next_instance_id = 1

    _scene_maps = []
    _next_scene_map_id = 1

    @classmethod
    def reset(cls):

        cls._pool = []
        cls._encounter = []

        cls._initiative = []
        cls._turn_index = 0
        cls._round_number = 1

        cls._next_pool_id = 1
        cls._next_instance_id = 1

        cls._scene_maps = []
        cls._next_scene_map_id = 1

    #
    # Session monster pool — independent, editable copies, never touch the
    # Monster Library. This is what lets a DM add "Zombie" and "Elite Zombie"
    # (same source monster, different stats) to the same session.
    #

    @classmethod
    def pool(cls):
        return list(cls._pool)

    @classmethod
    def add_to_pool(cls, name, hp, max_hp, ac, speed, xp, kind="monster", behavior="", abilities=""):

        entry = SessionMonster(
            pool_id=cls._next_pool_id,
            name=name,
            hp=hp,
            max_hp=max_hp,
            ac=ac,
            speed=speed,
            xp=xp,
            kind=kind,
            behavior=behavior,
            abilities=abilities,
        )

        cls._next_pool_id += 1
        cls._pool.append(entry)

        return entry

    @classmethod
    def remove_from_pool(cls, pool_id):

        cls._pool = [p for p in cls._pool if p.pool_id != pool_id]

    @classmethod
    def set_random_encounter(cls, pool_id, value):

        for entry in cls._pool:
            if entry.pool_id == pool_id:
                entry.random_encounter = value

    #
    # Live encounter
    #

    @classmethod
    def encounter(cls):
        return list(cls._encounter)

    @classmethod
    def _spawn_instance(cls, template):

        existing = sum(
            1 for m in cls._encounter if m.template_name == template.name
        )
        label = f"{template.name} #{existing + 1}"

        instance = MonsterInstance(
            instance_id=cls._next_instance_id,
            template_name=template.name,
            label=label,
            hp=template.hp,
            max_hp=template.max_hp,
            ac=template.ac,
            speed=template.speed,
            xp=template.xp,
            kind=template.kind,
            behavior=template.behavior,
            abilities=template.abilities,
        )

        cls._next_instance_id += 1
        cls._encounter.append(instance)

        return instance

    @classmethod
    def add_random_encounter(cls):

        candidates = [p for p in cls._pool if p.random_encounter]

        if not candidates:
            return None

        return cls._spawn_instance(random.choice(candidates))

    @classmethod
    def add_specific_encounter(cls, pool_id):

        template = next((p for p in cls._pool if p.pool_id == pool_id), None)

        if template is None:
            return None

        return cls._spawn_instance(template)

    @classmethod
    def remove_instance(cls, instance_id):

        cls._encounter = [
            m for m in cls._encounter if m.instance_id != instance_id
        ]

        removed_index = next(
            (
                i for i, entry in enumerate(cls._initiative)
                if entry.get("kind") == "monster"
                and entry.get("instance_id") == instance_id
            ),
            None
        )

        if removed_index is not None:

            cls._initiative.pop(removed_index)

            if removed_index < cls._turn_index:
                cls._turn_index -= 1
            elif cls._turn_index >= len(cls._initiative) and cls._initiative:
                cls._turn_index = 0

    @classmethod
    def _find_instance(cls, instance_id):

        for instance in cls._encounter:
            if instance.instance_id == instance_id:
                return instance

        return None

    @classmethod
    def damage_instance(cls, instance_id, amount):

        instance = cls._find_instance(instance_id)

        if instance:
            instance.hp = max(0, instance.hp - amount)

    @classmethod
    def heal_instance(cls, instance_id, amount):

        instance = cls._find_instance(instance_id)

        if instance:
            instance.hp = min(instance.max_hp, instance.hp + amount)

    #
    # Initiative
    #

    @classmethod
    def _roll_entries(cls, heroes):

        entries = []

        for hero in heroes:
            entries.append({
                "kind": "hero",
                "name": hero.name,
                "roll": random.randint(1, 20),
            })

        for instance in cls._encounter:
            entries.append({
                "kind": "monster",
                "instance_id": instance.instance_id,
                "label": instance.label,
                "roll": random.randint(1, 20),
            })

        entries.sort(key=lambda e: e["roll"], reverse=True)

        return entries

    @classmethod
    def roll_initiative(cls, heroes):

        cls._initiative = cls._roll_entries(heroes)
        cls._turn_index = 0
        cls._round_number = 1

    @classmethod
    def initiative_order(cls):
        return list(cls._initiative)

    @classmethod
    def current_turn(cls):

        if not cls._initiative:
            return None

        if cls._turn_index >= len(cls._initiative):
            return None

        return cls._initiative[cls._turn_index]

    @classmethod
    def next_turn(cls, heroes):

        if not cls._initiative:
            return

        cls._turn_index += 1

        if cls._turn_index >= len(cls._initiative):
            cls._round_number += 1
            cls._initiative = cls._roll_entries(heroes)
            cls._turn_index = 0

    @classmethod
    def round_number(cls):
        return cls._round_number

    #
    # Scene maps — this session's working set of maps, pulled from the
    # (global) Map Library. Ephemeral, session-scoped, never touches the
    # Library.
    #

    @classmethod
    def scene_maps(cls):
        return list(cls._scene_maps)

    @classmethod
    def add_scene_map(cls, name, path):

        entry = SceneMap(
            scene_map_id=cls._next_scene_map_id,
            name=name,
            path=path,
        )

        cls._next_scene_map_id += 1
        cls._scene_maps.append(entry)

        return entry

    @classmethod
    def remove_scene_map(cls, scene_map_id):

        cls._scene_maps = [
            m for m in cls._scene_maps if m.scene_map_id != scene_map_id
        ]
