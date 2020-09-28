import React, {Component} from 'react'
import store from "../_helpers/store";

import {
    CButton,
    CCol,
    CRow
} from '@coreui/react'

class TheHeaderStatus extends Component {
    constructor(props){
        super(props);
        this._isMounted = false;
        this.state = { status: 'disconnected' };

    }
    startSubscribe(){
        this.unsubscribe = store.subscribe(()=>{
            const status = store.getState().socketReducer.status;
            if (status !== this.state.status){
                this._isMounted && this.setState({status})
            }
        })
    }
    componentDidMount(){
        this._isMounted = true;
        this._isMounted && this.startSubscribe();

    }
    componentWillUnmount(){
        this._isMounted = false;
    }

    ButtonRender(props){
        if(props.status === 'connected'){
            return <CButton color="success" size="md" block>Connected</CButton>
        }
        return <CButton variant="outline" color="danger" size="md" block>Disconnected</CButton>


    }
    render () {
        return (
                <CRow className="align-items-center" style={{padding: "5px"}}>
                    {/*<CCol col="6" sm="4" md="2" xl className="mb-3 mb-xl-0">Connection: </CCol>*/}
                    <CCol col="6" sm="4" md="2" xl className="mb-3 mb-xl-0">
                        {/*{(function (){*/}
                            {/*switch (socketStatus){*/}
                                {/*case 'connected':*/}
                                    {/*return <CButton color="success" size="md" block>Connected</CButton>;*/}
                                {/*case 'disconnected':*/}
                                    {/*return <CButton variant="outline" color="danger" size="md" block>Disconnected</CButton>;*/}
                                {/*default:*/}
                                    {/*return <div>Error</div>*/}
                            {/*} })()}*/}
                        <this.ButtonRender status={this.state.status}/>
                    </CCol>
                </CRow>
        )
    }
}


export default TheHeaderStatus
