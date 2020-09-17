import React, {Component} from 'react'
import { Link } from 'react-router-dom'
import { connect } from 'react-redux';
import {callLogin, setLogin} from "../../../_actions";
import store from "../../../_helpers/store";
import {
  CButton,
  CCard,
  CCardBody,
  CCardGroup,
  CCol,
  CContainer,
  CForm,
  CInput,
  CInputGroup,
  CInputGroupPrepend,
  CInputGroupText,
  CRow
} from '@coreui/react'
import CIcon from '@coreui/icons-react'

class Login extends Component {
  constructor(props) {
    super(props);
    this.state = {
      UID: 'test',
      token: '' // TODO: Get token to Redux Store
    }

  }
  updateInputValue(evt){
    this.setState({ UID: evt.target.value });
  }
  handleClick(){
    store.dispatch(callLogin(this.state.UID))
    fetch("http://127.0.0.1:5000/auth/test", {
      method: "POST",
      crossDomain: true,
      credentials: 'include',
      headers: {
        "Content-Type": "application/json",
        "Accept": "application/json",
      },
      body: JSON.stringify({
        UID: this.state.UID,
      })
    }).then(response => response.json())
        .then((responseJson) => store.dispatch(setLogin(this.state.UID, responseJson)))

  }
  render()
  {

    return (
        <div className="c-app c-default-layout flex-row align-items-center">
          <CContainer>
            <CRow className="justify-content-center">
              <CCol md="8">
                <CCardGroup>
                  <CCard className="p-4">
                    <CCardBody>
                      <CForm>
                        <h1>Login</h1>
                        <p className="text-muted">Sign In to your account</p>
                        <CInputGroup className="mb-3">
                          <CInputGroupPrepend>
                            <CInputGroupText>
                              <CIcon name="cil-user"/>
                            </CInputGroupText>
                          </CInputGroupPrepend>
                          <CInput value={this.state.UID} onChange={evt => this.updateInputValue(evt)} type="text" placeholder="Username" autoComplete="username"/>
                        </CInputGroup>
                        {/*<CInputGroup className="mb-4">*/}
                        {/*  <CInputGroupPrepend>*/}
                        {/*    <CInputGroupText>*/}
                        {/*      <CIcon name="cil-lock-locked"/>*/}
                        {/*    </CInputGroupText>*/}
                        {/*  </CInputGroupPrepend>*/}
                        {/*  <CInput type="password" placeholder="Password" autoComplete="current-password"/>*/}
                        {/*</CInputGroup>*/}
                        <CRow>
                          <CCol xs="6">
                            <CButton onClick={() => this.handleClick()} color="primary" className="px-4">Login</CButton>
                          </CCol>

                        </CRow>
                      </CForm>
                    </CCardBody>
                  </CCard>
                  <CCard className="text-white bg-primary py-5 d-md-down-none" style={{width: '44%'}}>
                    <CCardBody className="text-center">
                      <div>
                        <h2>Sign up</h2>
                        <Link to="/register">
                          <CButton color="primary" className="mt-3" active tabIndex={-1}>Register Now!</CButton>
                        </Link>
                      </div>
                    </CCardBody>
                  </CCard>
                </CCardGroup>
              </CCol>
            </CRow>
          </CContainer>
        </div>
    )
  }
}
connect()(Login);

export {Login}