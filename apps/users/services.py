from apps.users.models import UserPreferences


class UserPreferencesService:
    def get_preferences(self, user):
        try:
            return UserPreferences.objects.get(user=user)
        except UserPreferences.DoesNotExist:
            return None
