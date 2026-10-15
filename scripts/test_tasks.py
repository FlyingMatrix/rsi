from mini_dgm.tasks import load_katas

katas = load_katas()
print(f"Loaded {len(katas)} kata(s):")
for k in katas:
    print(f"  - {k.id}  (entry={k.entry_point}, difficulty={k.difficulty}, tags={k.tags})")

k = katas[0]
print("\nagent_view keys:", list(k.agent_view().keys()))
print("hidden_tests exposed in agent_view? ", "hidden_tests" in k.agent_view())  # -> False
print("hidden tests visible in repr(kata)? ", "test_empty" in repr(k))           # -> False

"""
    > Output of running "python scripts\test_tasks.py":

        Loaded 1 kata(s):
        - rle_encode  (entry=encode, difficulty=easy, tags=('strings',))

        agent_view keys: ['id', 'spec', 'entry_point', 'public_tests']
        hidden_tests exposed in agent_view?  False
        hidden tests visible in repr(kata)?  False
"""