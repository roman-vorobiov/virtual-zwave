export default {
    template: `
        <div class="container p-0">
            <div class="row g-2">
                <div class="col-4 form-floating">
                    <input type="text" class="form-control" id="manufacturer-id-input" v-model.number="manufacturerId">
                    <label for="manufacturer-id-input">Manufacturer ID</label>
                </div>
                <div class="col-4 form-floating">
                    <input type="text" class="form-control" id="product-type-id-input" v-model.number="productTypeId">
                    <label for="product-type-id-input">Product Type ID</label>
                </div>
                <div class="col-4 form-floating">
                    <input type="text" class="form-control" id="product-id-input" v-model.number="productId">
                    <label for="product-id-input">Product ID</label>
                </div>
            </div>
        </div>
    `,

    data() {
        return {
            manufacturerId: 1,
            productTypeId: 2,
            productId: 3
        };
    },

    methods: {
        buildInfo() {
            return {
                classId: 0x72,
                version: 1,
                state: {
                    manufacturerId: this.manufacturerId,
                    productTypeId: this.productTypeId,
                    productId: this.productId
                }
            };
        }
    }
};
