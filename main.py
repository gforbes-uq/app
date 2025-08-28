import asyncio
from datetime import timedelta

from kelvin.application import KelvinApp, filters
from kelvin.krn import KRNAsset, KRNAssetDataStream
from kelvin.message import ControlChange, Recommendation, Number
from kelvin.message.evidences import Image, Markdown
from kelvin.logs import logger

async def main() -> None:
    """
    Start streaming asset data, monitor motor temperature vs. thresholds,
    and issue speed-reduction recommendations when necessary.
    """
    logger.info(f"Starting")
    app = KelvinApp()
    logger.info(f"KelvinApp() instance created")
    await app.connect()
    logger.info(f"app connected")


    # Process each incoming asset data message
    async for message in app.stream_filter(filters.is_asset_data_message):
        logger.info(f"Hello")
        asset_id = message.resource.asset
        data_stream = message.resource.data_stream

        # Track motor speed measurements for future use
        if data_stream == "mill_speed":
            current_mill_speed = message.payload

        # Retrieve configured multiplier for this asset
        multiplier = app.assets[asset_id].parameters.get("multiplier")

        new_speed_setpoint = current_mill_speed*multiplier
        logger.info(f"current_mill_speed: {current_mill_speed}")
        logger.info(f"multiplier: {multiplier}")
        logger.info(f"new_speed_setpoint: {new_speed_setpoint}")

        await app.publish(Number(
            resource=KRNAssetDataStream(asset_id, "output"),
            payload=new_speed_setpoint,
        )
        )

        await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())
