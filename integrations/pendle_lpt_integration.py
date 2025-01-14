from typing import Callable
import logging

from eth_typing import ChecksumAddress
from web3.contract import Contract

from constants.chains import Chain
from constants.pendle import PENDLE_USDE_JULY_DEPLOYMENT_BLOCK
from integrations.integration import Integration
from utils import pendle
from integrations.integration_ids import IntegrationID
from constants.summary_columns import SummaryColumn
from utils.pendle import get_pendle_participants_v3
from utils.web3_utils import call_with_retry


class PendleLPTIntegration(Integration):

    def __init__(
        self,
        integration_id: IntegrationID,
        start_block: int,
        sy_contract: Contract,
        lp_contract: Contract,
        get_participants_func: Callable[
            [list[ChecksumAddress]], set[str]
        ] = get_pendle_participants_v3,
        chain: Chain = Chain.ETHEREUM,
        summary_cols: list[SummaryColumn] | None = None,
        reward_multiplier: int = 1,
        balance_multiplier: int = 1,
        end_block: int | None = None,
        reward_multiplier_func: Callable[[int], int] | None = None,
    ):
        super().__init__(
            integration_id=integration_id,
            start_block=start_block,
            chain=chain,
            summary_cols=summary_cols,
            reward_multiplier=reward_multiplier,
            balance_multiplier=balance_multiplier,
            end_block=end_block,
            reward_multiplier_func=reward_multiplier_func,
        )
        self.sy_contract = sy_contract
        self.lp_contract = lp_contract
        self.summary_cols = (
            [SummaryColumn.PENDLE_SHARDS] if summary_cols is None else summary_cols
        )
        self.get_participants_func = get_participants_func

    def get_balance(self, user: str, block: int | str) -> float:
        logging.info(
            f"[{self.integration_id.get_description()}] Getting balance for {user} at block {block}"
        )
        sy_bal = call_with_retry(
            self.sy_contract.functions.balanceOf(self.lp_contract.address),
            block,
        )
        if sy_bal == 0:
            return 0
        lpt_bal = call_with_retry(
            self.lp_contract.functions.activeBalance(user),
            block,
        )
        if lpt_bal == 0:
            return 0
        total_active_supply = call_with_retry(
            self.lp_contract.functions.totalActiveSupply(),
            block,
        )
        if total_active_supply == 0:
            print("total_active_supply is 0")
            return 0

        print(
            f"sy_bal: {sy_bal}, lpt_bal: {lpt_bal}, total_active_supply: {total_active_supply}"
        )
        print(round(((sy_bal / 10**18) * lpt_bal) / total_active_supply, 4))
        return round(((sy_bal / 10**18) * lpt_bal) / total_active_supply, 4)

    def get_participants(self, blocks: list[int] | None) -> set[str]:
        if self.participants is not None:
            return self.participants

        logging.info(
            f"[{self.integration_id.get_description()}] Getting participants..."
        )
        self.participants = self.get_participants_func(
            [self.sy_contract.address, self.lp_contract.address]
        )
        logging.info(
            f"[{self.integration_id.get_description()}] Found {len(self.participants)} participants"
        )
        return self.participants


if __name__ == "__main__":
    integration = PendleLPTIntegration(
        IntegrationID.PENDLE_USDE_LPT,
        PENDLE_USDE_JULY_DEPLOYMENT_BLOCK,
        pendle.sy_contract,
        pendle.lpt_contract,
        reward_multiplier=20,
    )
    participants = integration.get_participants(None)
    print(participants)
    print(integration.get_balance(list(participants)[0], "latest"))
