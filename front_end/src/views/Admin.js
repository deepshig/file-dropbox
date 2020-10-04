import React from 'react'
import {Link} from 'react-router-dom'
import {
  CButton,
  CCard,
  CCardBody,
  CCardHeader,
  CCol,
  CRow
} from '@coreui/react'
import CIcon from '@coreui/icons-react'

const Admin = () => {
  return (
    <>
      <CCard>
        <CCardHeader>
          Admin Panels
        </CCardHeader>
        <CCardBody>
            <CRow className="align-items-center" style={{padding: '5px'}}>
                <CCol col="12" xl className="mb-3 mb-xl-0">
                    Postgres
                </CCol>
                <CCol col="6" sm="4" md="2" xl className="mb-3 mb-xl-0">
                    <a target="_blank" href={'http://localhost:8080'}> <CButton  block color="primary">Panel</CButton></a>
                </CCol>
                <CCol></CCol>
                <CCol></CCol>
            </CRow>
            <CRow className="align-items-center" style={{padding: '5px'}}>
                <CCol col="12" xl className="mb-3 mb-xl-0">
                    RabbitMQ
                </CCol>
                <CCol col="6" sm="4" md="2" xl className="mb-3 mb-xl-0">
                    <a target="_blank" href={'http://localhost:15672'}><CButton block color="primary">Panel</CButton></a>
                </CCol>
                <CCol></CCol>
                <CCol></CCol>
            </CRow>
        </CCardBody>
      </CCard>

    </>
  )
}

export default Admin
