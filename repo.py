from typing import Optional, NoReturn, Tuple, Set


class AliasSubscriptionsRepo:
    """Concrete implementation of AbstractAliasRepo"""
    _storage = {("vk.com", "milonga"): frozenset(["milonga", "mil"]),
                ("vk.com", "oldclothers"): frozenset(["old", "darom"]),
                ("vk.com", "kvartal_tango"): frozenset(["kv", "kvartal"])
                }

    def __new__(cls, *args, **kwargs):
        cls._ensure_have_no_duplicate_aliases()     # a single alias to various subscriptions is not allowed
        return super().__new__(cls)

    @classmethod
    def _ensure_have_no_duplicate_aliases(cls) -> Optional[NoReturn]:
        """
        Validates if there are only unique aliases in the storage.
        Sums number of aliases for each subscription and checks if the sum equals to len of the set of all aliases
        """
        total_len = sum(len(_) for _ in cls._storage.values())
        all_values = set()
        {all_values.update(_) for _ in cls._storage.values()}
        len_of_unique_values = len(all_values)
        if total_len == len_of_unique_values:
            return
        raise ValueError(f'Repo has ununique aliases')

    def get_subscription_info_by(self, alias: str) -> Tuple[str, str]:  # FIXME: consider return type
        """Returns service domain and subscription token by alias"""
        assert isinstance(alias, str)
        for subscription_info in self._storage:
            if alias in self._storage[subscription_info]:
                return subscription_info

        assert False, f'Have no such command: {alias}'

    def all_aliases_as_set(self) -> Set[str]:
        """Return all stored aliases as set"""
        all_values = set()
        return {all_values.update(_) for _ in self._storage.values()}
