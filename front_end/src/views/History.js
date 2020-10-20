import React, {Component} from 'react'
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
import store from "../_helpers/store";
import {receiveSocketMessage, sendSocketMessage} from "../_actions";

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

class History extends Component {
  constructor(props){
    super(props);
    this._isMounted = false;
    this.state = {
      payload: store.getState().socketReducer.payload,
      socketStatus: "On",
    };
    this.getHistory = this.getHistory.bind(this);
    this.getHistory();
  }
  getHistory(){
    store.dispatch(sendSocketMessage("get-history", {'user_id': store.getState().authentication.user_id}));
  };

  render () {
    return(
    <>
      <CRow>
        <CCol>
          <CCard>
            <CCardHeader>
              History
            </CCardHeader>
            <CCardBody>
              <CDataTable
                  items={usersData}
                  fields={fields}
                  hover
                  striped
                  bordered
                  size="sm"
                  itemsPerPage={15}
                  pagination
                  scopedSlots={{
                    'status':
                        (item) => (
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
}

export default History
