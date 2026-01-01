from enum import Enum
from typing import Any, Sequence, Type
from transitions import Machine, State, Event, EventData

class Phaser(Machine):
    def __init__(self, schedule: list):
        state_words = ["init"] + schedule.copy()
        state_objects = list()
        for name in state_words:
            state_objects.append(State(
                name=name,
                on_enter=["on_enter"]
            ))
        Machine.__init__(self, states=state_objects, initial="init", send_event=True)
        self.add_ordered_transitions(loop=False)

    def on_enter(self, event_data: EventData):
        print(event_data.transition.source, "->", event_data.transition.dest) # type: ignore

if __name__ == "__main__":
    p = Phaser(["a", "b"])
    p.next_state()
    p.next_state()
    print(p.state)
