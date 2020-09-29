import React, {Component, lazy} from 'react';
import store from '../../_helpers/store'
import {
    CButton,
    CCard,
    CCardBody,
    CCardFooter,
    CCardHeader,
    CCol,
    CRow,
    CForm, CFormGroup, CLabel, CInput, CFormText, CSelect, CInputFile

} from '@coreui/react';
import CIcon from '@coreui/icons-react'
import {sendSocketMessage} from "../../_actions";


class Dashboard extends Component {
    constructor(props){
        super(props);
        this._isMounted = false;
        this.state = {
            payload: store.getState().socketReducer.payload,
            socketStatus: "On"
        }
    }
    startSubscribe(){
        this.unsubscribe = store.subscribe(()=>{
            const payload = store.getState().socketReducer.payload;
            if (payload !== this.state.payload){
                this._isMounted && this.setState({payload});
            }
        });
    }
    componentDidMount(){
        this._isMounted = true;
        this._isMounted && this.startSubscribe();

    } // TODO: Not remounting and subscribing on refresh...
    componentWillUnmount(){
        this.unsubscribe();
        this._isMounted = false;
    }
    handleEmit=()=>{
        if(this.state.socketStatus==="On"){
            store.dispatch(sendSocketMessage("message", {'data':'Stop Sending', 'status':'Off'}));
            this.setState({'socketStatus':"Off"})
        }
        else{
            store.dispatch(sendSocketMessage("message", {'data':'Start Sending', 'status':'On'}));
            this.setState({'socketStatus':"On"})
        }
        console.log("Emit Clicked")
    };
    render () {
        const user = store.getState().authentication.user;
        return (

            <>
                <React.Fragment>
                    <div>
                        Socket Testing: {this.state.payload}
                        <div onClick={this.handleEmit}> Start/Stop</div>
                    </div>
                </React.Fragment>

                <CCard>
                    <CCardBody>
                        <CRow>
                            <CCol xs="12">
                                <CCard>
                                    <CCardHeader>
                                        Upload File(s)
                                        <small> Elements</small>
                                    </CCardHeader>
                                    <CCardBody>
                                        <CForm action="" method="post" encType="multipart/form-data"
                                               className="form-horizontal">
                                            <CFormGroup row>
                                                <CCol md="3">
                                                    <CLabel>Username</CLabel>
                                                </CCol>
                                                <CCol xs="12" md="9">
                                                    <p className="form-control-static">{ user
                                                        ? user
                                                        : 'Username'}</p>
                                                </CCol>
                                            </CFormGroup>
                                            <CFormGroup row>
                                                <CCol md="3">
                                                    <CLabel htmlFor="text-input">Text Input</CLabel>
                                                </CCol>
                                                <CCol xs="12" md="9">
                                                    <CInput id="text-input" name="text-input" placeholder="Text"/>
                                                    <CFormText>This is a help text</CFormText>
                                                </CCol>
                                            </CFormGroup>
                                            <CFormGroup row>
                                                <CCol md="3">
                                                    <CLabel htmlFor="date-input">Date Input</CLabel>
                                                </CCol>
                                                <CCol xs="12" md="9">
                                                    <CInput type="date" id="date-input" name="date-input"
                                                            placeholder="date"/>
                                                </CCol>
                                            </CFormGroup>
                                            <CFormGroup row>
                                                <CCol md="3">
                                                    <CLabel htmlFor="select">Select</CLabel>
                                                </CCol>
                                                <CCol xs="12" md="9">
                                                    <CSelect custom name="select" id="select">
                                                        <option value="0">Please select</option>
                                                        <option value="1">Option #1</option>
                                                        <option value="2">Option #2</option>
                                                        <option value="3">Option #3</option>
                                                    </CSelect>
                                                </CCol>
                                            </CFormGroup>
                                            <CFormGroup row>
                                                <CCol md="3">
                                                    <CLabel>Multiple File input</CLabel>
                                                </CCol>
                                                <CCol xs="12" md="9">
                                                    <CInputFile
                                                        id="file-multiple-input"
                                                        name="file-multiple-input"
                                                        multiple
                                                        custom
                                                    />
                                                    <CLabel htmlFor="file-multiple-input" variant="custom-file">
                                                        Choose Files...
                                                    </CLabel>
                                                </CCol>
                                            </CFormGroup>

                                        </CForm>
                                    </CCardBody>
                                    <CCardFooter>
                                        {user
                                            ?
                                            <div>
                                                <CButton type="submit" size="sm" color="primary"><CIcon
                                                name="cil-scrubber"/> Submit</CButton>
                                                <CButton type="reset" size="sm" color="danger"><CIcon
                                                name="cil-ban"/> Reset</CButton>
                                            </div>
                                            :
                                            <div>
                                                <CButton type="submit" size="sm" color="primary" disabled><CIcon
                                                    name="cil-scrubber"/> Submit</CButton>
                                                < CButton type="reset" size="sm" color="danger" disabled><CIcon
                                                name="cil-ban"/> Reset</CButton>
                                            </div>
                                        }
                                    </CCardFooter>
                                </CCard>

                            </CCol>
                        </CRow>
                    </CCardBody>
                </CCard>



            </>
        )
    }
}

export default Dashboard
