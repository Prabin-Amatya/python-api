from api.models import UserLevel
ul = UserLevel.objects.filter(level=1, exp=15).first()
if ul:
    ul.level = 2
    ul.exp = 0
    ul.save()
    print('Updated user to level 2')
else:
    print('User not found with 15 XP')
