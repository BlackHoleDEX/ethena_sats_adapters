from utils.web3_utils import W3_BY_CHAIN
import logging

from integrations.integration_ids import IntegrationID
from integrations.integration import Integration
from utils.radiant import get_radiant_lenders, get_effective_balance
from constants.radiant import (
    RADIANT_CONTRACTS_AND_START_BY_TOKEN,
    RadiantLendingDetails,
)


class RadiantIntegration(Integration):
    def __init__(self, integration_id: IntegrationID):
        self.vault_data: RadiantLendingDetails = RADIANT_CONTRACTS_AND_START_BY_TOKEN[
            integration_id
        ]

        print(self.vault_data)

        super().__init__(
            integration_id=integration_id,
            start_block=self.vault_data["start"],
            chain=self.vault_data["chain"],
            summary_cols=None,
            reward_multiplier=20,
        )

    def get_balance(self, user: str, block: int) -> float:
        return get_effective_balance(
            user,
            block,
            self.vault_data["collateral_address"],
            self.vault_data["r_token_contract"],
            self.vault_data["lending_pool"],
        )

    def get_participants(self, blocks: list[int] | None = None) -> set[str]:
        logging.info(
            f"[{self.integration_id.get_description()}] Getting participants..."
        )
        self.participants = get_radiant_lenders(
            self.vault_data["graph_url"],
            self.vault_data["collateral_address"],
        )

        return self.participants


if __name__ == "__main__":
    example_integration = RadiantIntegration(IntegrationID.RADIANT_USDE_CORE_ARBITRUM)
    current_block = W3_BY_CHAIN[example_integration.chain]["w3"].eth.get_block_number()

    print("Block:", current_block)
    print("Found Radiant Participants:")
    participants = example_integration.get_participants(None)
    print(len(participants))
    print("Found Balance of First Participant:", list(participants)[0])
    print(example_integration.get_balance(list(participants)[0], current_block))
