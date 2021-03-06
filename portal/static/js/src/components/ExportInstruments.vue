<template>
    <div>
        <div class="modal fade" id="dataDownloadModal" tabindex="-1" role="dialog">
            <div class="modal-dialog" role="document">
                <div class="modal-content">
                    <div class="modal-header">
                        <button type="button" class="close" data-dismiss="modal" :aria-label="closeLabel"><span aria-hidden="true">&times;</span></button>
                        <span v-text="title"></span>
                    </div>
                    <div class="modal-body">
                        <div class="form-group">
                            <label class="text-muted" v-text="instrumentsPromptLabel"></label>
                            <div id="patientsInstrumentListWrapper">
                                <!-- dynamically load instruments list -->
                                <div id="patientsInstrumentList" class="profile-radio-list"></div>
                                <div id="instrumentListLoad"><i class="fa fa-spinner fa-spin fa-2x loading-message"></i></div>
                            </div>
                        </div>
                        <div class="form-group">
                            <label class="text-muted" v-text="dataTypesPromptLabel"></label>
                            <div id="patientsDownloadTypeList" class="profile-radio-list">
                                <label class="radio-inline" v-for="item in dataTypes" :key="item.id">
                                    <input type="radio" name="downloadType" :id="item.id" :value="item.value" @click="setDataType" :checked="item.value == 'csv'"/>
                                    {{item.label}}
                                </label>
                            </div>
                        </div>
                        <br/>
                        <div id="instrumentsExportErrorMessage" class="error-message"></div>
                    </div>
                    <div class="modal-footer">
                        <a :href="getExportUrl()" class="btn btn-default" id="patientsDownloadButton" :disabled="!hasInstrumentsSelection()" v-text="exportLabel"></a>
                        <button type="button" class="btn btn-default" data-dismiss="modal" v-text="closeLabel"></button>
                    </div>
                </div>
            </div>
        </div>
        <div id="patientListExportDataContainer">
            <a href="#" id="patientAssessmentDownload"  class="btn btn-tnth-primary" data-toggle="modal" data-target="#dataDownloadModal"><span v-text="title" /></a>
        </div>
    </div>
</template>
<script>
    import tnthAjax from "../modules/TnthAjax.js";
    export default { /*global i18next */
        props: {
            instrumentsList: {
                type: Array,
                required: false
            }
        },
        data: function() {
            return {
                title: i18next.t("Export questionnaire data"),
                closeLabel: i18next.t("Close"),
                exportLabel: i18next.t("Export"),
                dataTypesPromptLabel: i18next.t("Data type:"),
                instrumentsPromptLabel: i18next.t("Instrument(s) to export data from:"),
                dataTypes: [
                    {
                        id: "csv_dataType",
                        value: "csv",
                        label: i18next.t("CSV")
                    },
                    {
                        id: "json_dataType",
                        value: "json",
                        label: i18next.t("JSON")
                    }
                ],
                instruments: {
                    list: [],
                    dataType: "csv",
                    selected: "",
                    message: ""
                }
            }
        },
        mounted: function() {
            this.getInstrumentList();
        },
        methods: {
            getInstrumentList: function () {
                if (this.instrumentsList && this.instrumentsList.length) {
                    this.setInstrumentsListContent(this.instrumentsList);
                    this.setInstrumentInputEvent();
                    return;
                }
                var self = this;
                tnthAjax.getInstrumentsList(false, function (data) {
                    if (!data || !data.length) {
                        document.querySelector("#instrumentsExportErrorMessage").innerText = data.error;
                        document.querySelector("#patientsInstrumentList").classList.add("ready");
                        return false;
                    }
                    document.querySelector("#instrumentsExportErrorMessage").innerText = "";
                    self.setInstrumentsListContent(data.sort());
                    setTimeout(function() {
                        self.setInstrumentInputEvent();
                    }.bind(self), 150);
                });
            },
            setInstrumentsListContent: function(list) {
                let content = "";
                (list).forEach(function(code) {
                    content += `<div class="checkbox instrument-container" id="${code}_container"><label><input type="checkbox" name="instrument" value="${code}">${code.replace(/_/g, " ").toUpperCase()}</label>`;
                });
                document.querySelector("#patientsInstrumentList").innerHTML = content;
                document.querySelector("#patientsInstrumentList").classList.add("ready");
            },
            setInstrumentInputEvent: function() {
                var self = this;
                $("#patientsInstrumentList [name='instrument']").on("click", function(event) {
                    if (event.target.value && $(event.target).is(":checked")) {
                        self.instruments.selected = self.instruments.selected + (self.instruments.selected !== "" ? "&" : "") + "instrument_id=" + event.target.value;
                        return;
                    }
                    if ($("input[name=instrument]:checked").length === 0) {
                        self.instruments.selected = "";
                    }
                });
                $("#dataDownloadModal").on("show.bs.modal", function () {
                    self.instruments.selected = "";
                    self.instruments.dataType = "csv";
                    $("#patientsInstrumentList").addClass("ready");
                    $(this).find("[name='instrument']").prop("checked", false);
                });
            },
            setDataType: function (event) {
                this.instruments.showMessage = false;
                this.instruments.dataType = event.target.value;
            },
            getExportUrl: function() {
                return `/api/patient/assessment?${this.instruments.selected}&format=${this.instruments.dataType}`;
            },
            hasInstrumentsSelection: function () {
                return this.instruments.selected !== "" && this.instruments.dataType !== "";
            }
        }
    };
</script>
