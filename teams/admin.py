from django.contrib import admin
from .models import Team, TeamInviteCode, TeamMembershipRequest

admin.site.register(Team)
admin.site.register(TeamInviteCode)
admin.site.register(TeamMembershipRequest)
