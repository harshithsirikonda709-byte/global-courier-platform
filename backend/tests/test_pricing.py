import unittest

import httpx

from app.main import app
from app.schemas.booking import ParcelCategory
from app.services.pricing import (
    BASE_FEE,
    CATEGORY_SURCHARGES,
    INTERSTATE_SURCHARGE,
    PACKAGING_SURCHARGES,
    RATE_PER_EXTRA_KG,
    calculate_pricing,
    calculate_volumetric_weight,
)


class PricingEngineTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.client = httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver")
        self.addAsyncCleanup(self.client.aclose)

    def test_volumetric_weight_formula(self):
        # 50cm x 40cm x 30cm = 60,000 / 5000 = 12.0 kg
        vol = calculate_volumetric_weight(50.0, 40.0, 30.0)
        self.assertEqual(vol, 12.0)

    def test_pricing_uses_greater_chargeable_weight(self):
        # Actual weight 5.0 kg, Volumetric (50x40x30)/5000 = 12.0 kg -> Chargeable = 12.0 kg
        res = calculate_pricing(
            weight_kg=5.0,
            length_cm=50.0,
            width_cm=40.0,
            height_cm=30.0,
            category=ParcelCategory.GENERAL,
        )
        self.assertEqual(res.chargeable_weight_kg, 12.0)
        self.assertEqual(res.volumetric_weight_kg, 12.0)

        # Base fee (50.0) + Extra weight (11.5 kg * 40 = 460.0) = 510.0
        # GST 18% = 91.80 -> Total = 601.80
        self.assertEqual(res.base_fee, BASE_FEE)
        self.assertEqual(res.weight_fee, 460.0)
        self.assertEqual(res.subtotal, 510.0)
        self.assertEqual(res.tax_amount, 91.80)
        self.assertEqual(res.total_price, 601.80)

    def test_category_surcharges(self):
        # Electronics surcharge is +100
        res_elec = calculate_pricing(
            weight_kg=0.4,
            length_cm=10.0,
            width_cm=10.0,
            height_cm=10.0,
            category=ParcelCategory.ELECTRONICS,
        )
        self.assertEqual(res_elec.category_surcharge, CATEGORY_SURCHARGES[ParcelCategory.ELECTRONICS])
        # Fragile surcharge is +150
        res_fragile = calculate_pricing(
            weight_kg=0.4,
            length_cm=10.0,
            width_cm=10.0,
            height_cm=10.0,
            category=ParcelCategory.FRAGILE,
        )
        self.assertEqual(res_fragile.category_surcharge, CATEGORY_SURCHARGES[ParcelCategory.FRAGILE])

    def test_packaging_surcharges(self):
        res_crating = calculate_pricing(
            weight_kg=1.0,
            length_cm=10.0,
            width_cm=10.0,
            height_cm=10.0,
            category=ParcelCategory.GENERAL,
            packaging_status="CUSTOM_CRATING",
        )
        self.assertEqual(res_crating.packaging_surcharge, PACKAGING_SURCHARGES["CUSTOM_CRATING"])

    def test_interstate_surcharge(self):
        # Same state: no surcharge
        res_intra = calculate_pricing(
            weight_kg=1.0,
            length_cm=10.0,
            width_cm=10.0,
            height_cm=10.0,
            category=ParcelCategory.GENERAL,
            pickup_state="Telangana",
            receiver_state="Telangana",
        )
        self.assertEqual(res_intra.interstate_fee, 0.0)

        # Inter-state: +80 surcharge
        res_inter = calculate_pricing(
            weight_kg=1.0,
            length_cm=10.0,
            width_cm=10.0,
            height_cm=10.0,
            category=ParcelCategory.GENERAL,
            pickup_state="Telangana",
            receiver_state="Karnataka",
        )
        self.assertEqual(res_inter.interstate_fee, INTERSTATE_SURCHARGE)

    async def test_pricing_calculate_api_endpoint(self):
        payload = {
            "weight_kg": 2.5,
            "length_cm": 30.0,
            "width_cm": 20.0,
            "height_cm": 15.0,
            "category": "electronics",
            "packaging_status": "REPACKAGED",
            "pickup_state": "Telangana",
            "receiver_state": "Karnataka",
        }
        response = await self.client.post("/api/v1/pricing/calculate", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("total_price", data)
        self.assertIn("subtotal", data)
        self.assertIn("tax_amount", data)
        self.assertEqual(data["packaging_surcharge"], 50.0)
        self.assertEqual(data["category_surcharge"], 100.0)
        self.assertEqual(data["interstate_fee"], 80.0)
        self.assertGreater(data["total_price"], 0)


if __name__ == "__main__":
    unittest.main()
