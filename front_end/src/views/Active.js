import React from 'react'
import {
  CBadge,
  CCard,
  CCardBody,
  CCardHeader,
  CCol,
  CDataTable,
  CRow
} from '@coreui/react'

import usersData from './users/UsersData'

const getBadge = status => {
  switch (status) {
    case 'Active': return 'success'
    case 'Inactive': return 'secondary'
    case 'Pending': return 'warning'
    case 'Banned': return 'danger'
    default: return 'primary'
  }
}
const fields = ['name','registered', 'role', 'status']

const Active = () => {
  return (
    <>
      <CRow>
        <CCol xs="12" lg="6">
          <CCard>
            <CCardHeader>
              Node 1
            </CCardHeader>
            <CCardBody>
            <CDataTable
              items={usersData}
              fields={fields}
              itemsPerPage={5}
              pagination
              scopedSlots = {{
                'status':
                  (item)=>(
                    <td>
                      <CBadge color={getBadge(item.status)}>
                        {item.status}
                      </CBadge>
                    </td>
                  )

              }}
            />
            </CCardBody>
          </CCard>
        </CCol>

          <CCol xs="12" lg="6">
              <CCard>
                  <CCardHeader>
                      Node 2
                  </CCardHeader>
                  <CCardBody>
                      <CDataTable
                          items={usersData}
                          fields={fields}
                          itemsPerPage={5}
                          pagination
                          scopedSlots = {{
                              'status':
                                  (item)=>(
                                      <td>
                                          <CBadge color={getBadge(item.status)}>
                                              {item.status}
                                          </CBadge>
                                      </td>
                                  )

                          }}
                      />
                  </CCardBody>
              </CCard>
          </CCol>
      </CRow>

      <CRow>

          <CCol xs="12" lg="6">
              <CCard>
                  <CCardHeader>
                      Node 3
                  </CCardHeader>
                  <CCardBody>
                      <CDataTable
                          items={usersData}
                          fields={fields}
                          itemsPerPage={5}
                          pagination
                          scopedSlots = {{
                              'status':
                                  (item)=>(
                                      <td>
                                          <CBadge color={getBadge(item.status)}>
                                              {item.status}
                                          </CBadge>
                                      </td>
                                  )

                          }}
                      />
                  </CCardBody>
              </CCard>
          </CCol>

          <CCol xs="12" lg="6">
              <CCard>
                  <CCardHeader>
                      Node 4
                  </CCardHeader>
                  <CCardBody>
                      <CDataTable
                          items={usersData}
                          fields={fields}
                          itemsPerPage={5}
                          pagination
                          scopedSlots = {{
                              'status':
                                  (item)=>(
                                      <td>
                                          <CBadge color={getBadge(item.status)}>
                                              {item.status}
                                          </CBadge>
                                      </td>
                                  )

                          }}
                      />
                  </CCardBody>
              </CCard>
          </CCol>

      </CRow>

    </>
  )
}

export default Active
