<template>
  <div class="modal fade" id="completionModal" tabindex="-1" aria-labelledby="completionModalLabel" aria-hidden="true">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="completionModalLabel">Complete Appointment</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="submitForm">
            <div class="mb-3">
              <label for="diagnosis" class="form-label">Diagnosis</label>
              <textarea class="form-control" id="diagnosis" v-model="form.diagnosis" rows="3"></textarea>
            </div>
            <div class="mb-3">
              <label for="prescription" class="form-label">Prescription</label>
              <textarea class="form-control" id="prescription" v-model="form.prescription" rows="3"></textarea>
            </div>
            <div class="mb-3">
              <label for="notes" class="form-label">Notes</label>
              <textarea class="form-control" id="notes" v-model="form.notes" rows="2"></textarea>
            </div>
            <hr />
            <h6>Readmission Risk Inputs</h6>
            <div class="row g-2">
              <div class="col-md-6">
                <label for="timeInHospital" class="form-label">Days in Hospital</label>
                <input type="number" min="0" class="form-control" id="timeInHospital" v-model.number="form.readmission_features.time_in_hospital" />
              </div>
              <div class="col-md-6">
                <label for="numMeds" class="form-label">No. of Medications</label>
                <input type="number" min="0" class="form-control" id="numMeds" v-model.number="form.readmission_features.num_medications" />
              </div>
              <div class="col-md-6">
                <label for="labProcedures" class="form-label">Lab Procedures</label>
                <input type="number" min="0" class="form-control" id="labProcedures" v-model.number="form.readmission_features.num_lab_procedures" />
              </div>
              <div class="col-md-6">
                <label for="activeMeds" class="form-label">Active Medications Count</label>
                <input type="number" min="0" class="form-control" id="activeMeds" v-model.number="form.readmission_features.active_med_count" />
              </div>
              <div class="col-md-6">
                <label for="comorbidity" class="form-label">Comorbidity Score</label>
                <input type="number" min="0" class="form-control" id="comorbidity" v-model.number="form.readmission_features.comorbidity_score" />
              </div>
              <div class="col-md-6">
                <label for="a1c" class="form-label">A1C Abnormal</label>
                <select class="form-select" id="a1c" v-model.number="form.readmission_features.a1c_abnormal">
                  <option :value="0">No</option>
                  <option :value="1">Yes</option>
                </select>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
              <button type="submit" class="btn btn-primary">Save</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "CompletionModal",
  data() {
    return {
      form: {
        diagnosis: "",
        prescription: "",
        notes: "",
        readmission_features: {
          time_in_hospital: 3,
          num_medications: 1,
          num_lab_procedures: 20,
          active_med_count: 1,
          comorbidity_score: 1,
          a1c_abnormal: 0
        }
      }
    };
  },
  methods: {
    submitForm() {
      this.$emit("submit", this.form);
    }
  }
};
</script>