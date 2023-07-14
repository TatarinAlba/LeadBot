from model import Account, Category, Account_by_category, SessionMaker


class AccountRepository:
    __session = SessionMaker()

    def getAllAcounts(self):
        with AccountRepository.__session as session:
            accounts = session.query(Account).all()
        return accounts

    def getAccountById(self, account_telegram_id: int):
        try:
            with AccountRepository.__session as session:
                account = (
                    session.query(Account)
                    .filter(Account.account_telegram_id == account_telegram_id)
                    .all()[0]
                )
        except IndexError:
            return None
        return account

    def removeAccount(self, account: Account):
        try:
            with AccountRepository.__session as session:
                account = (
                    session.query(Account)
                    .filter(Account.account_telegram_id == account.account_telegram_id)
                    .all()[0]
                )
                session.delete(account)
                session.commit()
        except IndexError:
            return False
        return True

    def addAccount(self, account: Account):
        with AccountRepository.__session as session:
            session.add(account)
            session.commit()
        return True

    def updateAccount(self, account: Account):
        with AccountRepository.__session as session:
            session.query(Account).filter(
                Account.account_telegram_id == account.account_telegram_id
            ).update({Account.name: account.name, Account.password: account.password})
            session.commit()
        return account


class CategoryRepository:
    __session = SessionMaker()

    def getCategoryByName(self, name: str):
        try:
            with CategoryRepository.__session as session:
                category = (
                    session.query(Category)
                    .filter(Category.category_name == name)
                    .all()[0]
                )
        except IndexError:
            return None
        return category

    def removeCategory(self, category: Category):
        try:
            with CategoryRepository.__session as session:
                account = (
                    session.query(Category)
                    .filter(Category.category_name == category.category_name)
                    .all()[0]
                )
                session.delete(account)
                session.commit()
        except IndexError:
            return False
        return True

    def addCategory(self, category: Category):
        with CategoryRepository.__session as session:
            session.add(category)
            session.commit()
        return True


class AccountWithCategoryRepository:
    __session = SessionMaker()

    def turnOffAllCategoriesForAccount(self, account_telegram_id: int):
        with AccountWithCategoryRepository.__session as session:
            session.query(Account_by_category).filter(
                Account_by_category.account_telegram_id == account_telegram_id
            ).update({Account_by_category.is_enabled_for_search: False})
            session.commit()
        return True

    def turnOnAllCategoriesForAccount(self, account_telegram_id: int):
        with AccountWithCategoryRepository.__session as session:
            session.query(Account_by_category).filter(
                Account_by_category.account_telegram_id == account_telegram_id
            ).update({Account_by_category.is_enabled_for_search: True})
            session.commit()
        return True

    def getAccountsForCategoryByName(self, categoryName: str):
        try:
            with AccountWithCategoryRepository.__session as session:
                category: Category = (
                    session.query(Category)
                    .filter(Category.category_name == categoryName)
                    .all()[0]
                )
                accounts = (
                    session.query(Account_by_category)
                    .filter(Category.category_name == category.category_name)
                    .all()
                )
        except IndexError:
            return None
        return accounts

    def getAccountForCategoryByName(self, category_name: str):
        try:
            with AccountWithCategoryRepository.__session as session:
                category: Category = (
                    session.query(Category)
                    .filter(Category.category_name == category_name)
                    .all()[0]
                )
                account = (
                    session.query(Account_by_category)
                    .filter(Category.category_name == category.category_name)
                    .all()[0]
                )
        except IndexError:
            return None
        return account

    def removeAccountsForCategory(self, account: Account_by_category):
        try:
            with AccountWithCategoryRepository.__session as session:
                account = (
                    session.query(Account_by_category)
                    .filter(
                        Account_by_category.account_telegram_id
                        == account.account_telegram_id,
                        Account_by_category.category_id == account.category_id,
                    )
                    .all()[0]
                )
                session.delete(account)
                session.commit()
        except IndexError:
            return False
        return True

    def addAccountForCategory(self, account: Account_by_category):
        try:
            with AccountWithCategoryRepository.__session as session:
                session.add(account)
                session.commit()
        except Exception as e:
            print(e)
        return True
