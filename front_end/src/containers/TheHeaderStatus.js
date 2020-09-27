import React, {Component} from 'react'
import store from "../_helpers/store";

import {
    CButton,
    CCol,
    CRow
} from '@coreui/react'

class TheHeaderStatus extends Component {
    ButtonRender(props){
        if(props.status === 'connected'){
            return <CButton variant="outline" color="info" size="md" block>Connected</CButton>
        }
        if (props.status === 'connecting'){
            return <CButton variant="outline" color="warning" size="md" block>Connecting</CButton>
        }
        return <CButton variant="outline" color="danger" size="md" block>Disconnected</CButton>

    }
    render () {
        const socketStatus = store.getState().socketReducer.status;
        return (
                <CRow className="align-items-center" style={{padding: "5px"}}>
                    {/*<CCol col="6" sm="4" md="2" xl className="mb-3 mb-xl-0">Connection: </CCol>*/}
                    <CCol col="6" sm="4" md="2" xl className="mb-3 mb-xl-0">
                        <this.ButtonRender status={socketStatus}/>
                    </CCol>
                </CRow>
        )
    }
}


export default TheHeaderStatus
