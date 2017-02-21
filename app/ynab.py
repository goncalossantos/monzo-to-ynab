import logging
from datetime import datetime

from pynYNAB.Client import nYnabConnection, nYnabClient, BudgetNotFound
from pynYNAB.schema.budget import Payee, Transaction

log = logging.getLogger(__name__)


class InvalidYnabSettings(Exception):
    pass


class YNAB(object):
    def __init__(self, username, password, budget_name):

        self.username = username
        self.password = password
        self.budget_name = budget_name

        self.client = self.get_client()

    def get_client(self):
        conn = nYnabConnection(self.username, self.password)
        try:
            client = nYnabClient(nynabconnection=conn, budgetname=self.budget_name)
            return client
        except BudgetNotFound:
            raise InvalidYnabSettings("No Budged with that name")

    @property
    def accounts(self):
        return {x.account_name: x for x in self.client.budget.be_accounts}

    @property
    def payees(self):
        return {p.name: p for p in self.client.budget.be_payees}

    def get_account(self, account_name):
        try:
            log.debug('searching for account %s' % account_name)
            return self.accounts[account_name]
        except KeyError:
            log.error("Couldn't find this account: %s" % account_name)
            exit(-1)

    def get_payee(self, payee_name):
        try:
            log.debug('searching for payee %s' % payee_name)
            return self.payees[payee_name]
        except KeyError:
            log.debug('Couldn''t find this payee: %s' % payee_name)
            payee = self.create_payee(payee_name)
            return payee

    # noinspection PyArgumentList
    def create_payee(self, payee_name):
        payee = Payee(name=payee_name)
        self.client.budget.be_payees.append(payee)
        return payee

    # noinspection PyArgumentList,PyArgumentList,PyArgumentList,PyArgumentList,PyArgumentList,PyArgumentList,
    # PyArgumentList
    # noinspection PyArgumentList
    def create_transaction(self, account_id, payee_id, date, amount, memo, imported_payee):
        transactions = []
        transaction = Transaction(
            entities_account_id=account_id,
            amount=amount,
            date=date,
            entities_payee_id=payee_id,
            imported_date=datetime.now().date(),
            imported_payee=imported_payee,
            memo=memo,
            source="Imported"
        )
        transactions.append(transaction)
        return transactions

    def add_transactions(self, transactions):

        for transaction in transactions:
            self.client.budget.be_transactions.append(transaction)
        catalog_changed_entities = self.client.catalog.get_changed_apidict()
        budget_changed_entities = self.client.budget.get_changed_apidict()

        delta = sum(len(l) for k, l in catalog_changed_entities.items()) + \
            sum(len(l) for k, l in budget_changed_entities.items())
        self.client.push(delta)
