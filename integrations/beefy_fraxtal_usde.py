from constants.chains import Chain
from integrations.integration_ids import IntegrationID
from utils.beefy import BeefyIntegration

if __name__ == "__main__":
    beefy_integration = BeefyIntegration(
        IntegrationID.BEEFY_FRAXTAL_USDE, 2366784, Chain.FRAXTAL
    )
    print(beefy_integration.get_participants(None))
    print(
        beefy_integration.get_balance(
            list(beefy_integration.get_participants(None))[0], 2466784
        )
    )
