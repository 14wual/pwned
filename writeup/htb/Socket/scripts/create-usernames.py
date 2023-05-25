import itertools

def generate_usernames(full_name):
    full_name = full_name.lower()
    names = full_name.split()
    initials = [n[0] for n in names]
    last_name = names[-1]

    combinations = []
    for r in range(1, len(initials) + 1):combinations.extend(list(itertools.combinations(initials, r)))

    usernames = []

    for combo in combinations:
        username = "".join(combo) + last_name
        usernames.append(username)

    return usernames

full_name = "Thomas Keller"
usernames = generate_usernames(full_name)

for username in usernames:print(username)
